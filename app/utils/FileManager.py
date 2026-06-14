import os
import uuid
import shutil

def delete_old_image(image_path):
    if not image_path:
        return

    file_path = image_path.lstrip("/")

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")


def save_file(file, folder_name):
    upload_dir = f"static/{folder_name}"
    os.makedirs(upload_dir, exist_ok=True)

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    path = os.path.join(upload_dir, filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/static/{folder_name}/{filename}"
