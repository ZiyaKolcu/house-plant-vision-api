from datetime import datetime
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from api.db.database import Database
from api.utils.image_utils import save_uploaded_file, open_image
from api.utils.logger import log_usage

# Load model
model = AutoModelForImageClassification.from_pretrained("houseplant_model")
processor = AutoImageProcessor.from_pretrained("houseplant_model")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


async def save_image(file):
    return await save_uploaded_file(file)


async def insert_submission_to_db(current_user, file_path):
    insert_submission = """
        INSERT INTO photo_submissions (user_id, image_url, submitted_at)
        VALUES (%s, %s, %s) RETURNING id
    """
    now = datetime.now()
    row = await Database.fetchrow(insert_submission, current_user, file_path, now)
    return row["id"]


async def predict_species(file_path):
    image = open_image(file_path)
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    predicted_idx = logits.argmax(-1).item()
    confidence = float(torch.softmax(logits, dim=-1)[0, predicted_idx].cpu())

    return predicted_idx, confidence


async def lookup_species(predicted_idx):
    species_query = """
        SELECT id, scientific_name, common_name
        FROM plant_species
        WHERE id = %s
    """
    species_row = await Database.fetchrow(species_query, predicted_idx + 1)
    if species_row:
        return (
            species_row["id"],
            species_row["scientific_name"],
            species_row["common_name"],
        )
    return None, None, None


async def insert_prediction_to_db(submission_id, species_id, confidence, now):
    insert_prediction = """
        INSERT INTO predictions
        (submission_id, species_id, confidence_score, predicted_at, model_version)
        VALUES (%s, %s, %s, %s, %s)
    """
    await Database.execute(
        insert_prediction,
        submission_id,
        species_id,
        confidence,
        now,
        "v1.0",
    )


async def update_submission_status(submission_id, status):
    update_status = """
        UPDATE photo_submissions
        SET status = %s
        WHERE id = %s
    """
    await Database.execute(update_status, status, submission_id)


async def handle_submission(file, current_user):
    try:
        file_path = await save_image(file)
        submission_id = await insert_submission_to_db(current_user, file_path)
        predicted_idx, confidence = await predict_species(file_path)
        species_id, scientific_name, common_name = await lookup_species(predicted_idx)
        now = datetime.now()
        await insert_prediction_to_db(submission_id, species_id, confidence, now)
        await update_submission_status(submission_id, "processed")

        return {
            "submission_id": submission_id,
            "species_id": species_id,
            "scientific_name": scientific_name,
            "common_name": common_name,
            "confidence": confidence,
        }

    except Exception as e:
        await log_usage(current_user, "submit_photo", "failed", str(e))
        raise
