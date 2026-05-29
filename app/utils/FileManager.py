import os
from fastapi import UploadFile
import uuid
import shutil
from core.config import settings

def delete_old_image(image_path):
    if not image_path:
        return

    file_path = image_path.lstrip("/")

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")


def save_file(image_file: UploadFile) -> str:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    ext = image_file.filename.split(".")[-1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    disk_path = os.path.join(settings.UPLOAD_DIR, filename)

    with open(disk_path, "wb") as buffer:
        shutil.copyfileobj(image_file.file, buffer)

    return f"{settings.UPLOAD_URL_PREFIX}/{filename}"
