from datetime import datetime
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from api.db.database import Database
from api.utils.image_utils import save_uploaded_file, open_image

# Load model
model = AutoModelForImageClassification.from_pretrained("houseplant_model")
processor = AutoImageProcessor.from_pretrained("houseplant_model")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


async def handle_submission(file, current_user):
    # Save image
    file_path = await save_uploaded_file(file)

    # Insert initial submission
    insert_submission = """
        INSERT INTO photo_submissions (user_id, image_url, submitted_at)
        VALUES (%s, %s, %s) RETURNING id
    """
    now = datetime.now()
    row = await Database.fetchrow(insert_submission, current_user, file_path, now)
    submission_id = row["id"]

    # Inference
    image = open_image(file_path)
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_idx = logits.argmax(-1).item()
    confidence = float(torch.softmax(logits, dim=-1)[0, predicted_idx].cpu())

    # Species lookup
    species_query = """
        SELECT id, scientific_name, common_name
        FROM plant_species
        WHERE id = %s
    """
    species_row = await Database.fetchrow(species_query, predicted_idx + 1)
    species_id = species_row["id"] if species_row else None
    scientific_name = species_row["scientific_name"] if species_row else None
    common_name = species_row["common_name"] if species_row else None

    # Insert prediction
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

    # Update status
    update_status = """
        UPDATE photo_submissions
        SET status = %s
        WHERE id = %s
    """
    await Database.execute(update_status, "processed", submission_id)

    return {
        "submission_id": submission_id,
        "species_id": species_id,
        "scientific_name": scientific_name,
        "common_name": common_name,
        "confidence": confidence,
    }
