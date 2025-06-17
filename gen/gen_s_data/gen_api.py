from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import os
import io
import zipfile
from fastapi import Path
import logging


# CREATING LOGGER
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


app = FastAPI()

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
@app.get("/files/zip/{folder_name}")
def get_files_zip(folder_name: str = Path(..., regex="^(invoices|receipts)$")):
    target_folder = os.path.join(DATA_FOLDER, folder_name)
    if not os.path.isdir(target_folder):
        raise HTTPException(status_code=404, detail="Specified folder not found")

    # Collect all files in the directory
    files = [
        f for f in os.listdir(target_folder)
        if os.path.isfile(os.path.join(target_folder, f))
    ]
    if not files:
        raise HTTPException(status_code=404, detail=f"No files found in specified folder {target_folder}")

    # Create a zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for filename in files:
            file_path = os.path.join(target_folder, filename)
            zip_file.write(file_path, arcname=filename)
    zip_buffer.seek(0)
    logger.info(f"Zipped {len(files)} files from folder '{folder_name}'")
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={folder_name}_files.zip"}
    )

@app.get("/health")
def health():
    return {"status": "ok"}
    
    