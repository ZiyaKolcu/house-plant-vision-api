import os
import uuid
from PIL import Image


async def save_uploaded_file(file, upload_dir="uploads"):
    os.makedirs(upload_dir, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(upload_dir, unique_name)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return file_path


def open_image(path):
    return Image.open(path).convert("RGB")
