from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path 
import os
import io
import zipfile
# from fastapi import Path
import logging
from datetime import datetime


# CREATING LOGGER
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


app = FastAPI()

BASE_DIR = Path(os.path.dirname(__file__), "data")

@app.get("/files/zip/{file_format}/{datetime_from_which_to_pull}")
def get_zip_files(file_format: str, datetime_from_which_to_pull: str):
    try:
        # Parse the datetime string
        from_dt = datetime.strptime(datetime_from_which_to_pull, "%Y%m%dT%H%M%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format. Use YYYYMMDDTHHMMSS.")

    # Define the directory path
    dir_path = BASE_DIR / file_format
    if not dir_path.exists() or not dir_path.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found.")

    # Find matching files
    matching_files = []
    for file in dir_path.glob(f"{file_format[:-1]}_*"):  # 'invoice_*' or 'receipt_*'
        try:
            dt_str = file.stem.lstrip(f"{file_format[:-1]}_")
            # logger.info(f'dt_str: {dt_str}')
            file_dt = datetime.strptime(dt_str, '%Y_%m_%d__%H:%M:%S')
            if file_dt >= from_dt:
                # logger.info('FILE ADDED TO ZIP')
                matching_files.append(file)
        except (IndexError, ValueError) as e:
            logger.error(f'ERROR {e} OCCURED - SKIPPING RECORD')
            continue  # Skip malformed filenames

    if not matching_files:
        raise HTTPException(status_code=404, detail="No matching files found.")

    # Create zip in-memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in matching_files:
            zipf.write(file_path, arcname=file_path.name)
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={file_format}_files.zip"}
    )
@app.get("/health")
def health():
    return {"status": "ok"}
    
    