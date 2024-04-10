import os
import base64
from fastapi import UploadFile
from fastapi.responses import FileResponse

def save_image_as_png(folder: str, image: UploadFile, id: int):
    if not folder.startswith("/"):
        folder = f"/{folder}"
    folder = os.getenv("STATIC_FOLDER") + folder
    
    # If the folder doesn't exists, we create
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Save image (the filename will be the id)
    with open(os.path.join(folder, str(id) + ".png"), "wb") as buffer:
        buffer.write(image.file.read())
        
def get_image_as_byte_64(folder: str, id: int):
    if not folder.startswith("/"):
        folder = f"/{folder}"
    folder = os.getenv("STATIC_FOLDER") + folder
        
    image_path = os.path.join(folder, str(id) + ".png")
    
    if not os.path.exists(image_path):
        return None
    else:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
        
def get_image_as_file_response(folder: str, id: int):
    if not folder.startswith("/"):
        folder = f"/{folder}"
        
    folder = os.getenv("STATIC_FOLDER") + folder
        
    image_path = os.path.join(folder, str(id) + ".png")
    if not os.path.exists(image_path):
        return None
    else:
        return FileResponse(image_path)