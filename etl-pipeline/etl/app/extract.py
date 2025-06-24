import requests
import xml, json
import io
import zipfile
import logging
from datetime import datetime
import pathlib, os

# CREATING LOGGER
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

TMP_DATA_DIR = os.path.join('tmp', 'data')
pathlib.Path(TMP_DATA_DIR).mkdir(parents=True, exist_ok=True)


def get_files_url(url: str):
    """Extract files from url and save to TMP_DATA_DIR

    Args:
        url (str): the URL to extract from
    """
    response = requests.get(url)

    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            logger.info(f'Extracted {z} from {url}')
            z.extractall(TMP_DATA_DIR)
    else:
        logger.error(f"Failed to download: {response.status_code} - {response.text}")

def extract_files_url(url_s_conn_info: list[dict]):
    
    # CREATE URLS
    try:
        # create urls fetching data from the LAST HOUR !!!
        one_hour_ago = datetime.now().replace(minute=0, second=0, microsecond=0)  # round to hour
        one_hour_ago = one_hour_ago.replace(hour=one_hour_ago.hour - 1 if one_hour_ago.hour > 0 else 23)
        date_str = one_hour_ago.strftime('%Y%m%dT%H0000')
        urls_list = [
            f"http://{conn_info['host']}:{str(conn_info['port'])}/files/zip/{doctype}/{date_str}"
            for conn_info in url_s_conn_info
            for doctype in conn_info['doc_type']
        ]
    except KeyError as ke:
        logger.error(f'BAD URL DECLARETION, TO FIX {ke}')
        urls_list = []
    
    # WHAT IF NOTHING HAPPENS IN AN HOUR?
    # Do not extract - terminate
    if not urls_list:
        #TODO: THINK OF TERMINATION
        # raise RuntimeError()
        logger.error("NO DOCUMENTS PULLED")
        raise RuntimeError("NO DOCUMENTS PULLED")
    
    # Extract files to TMP_dir
    for url in urls_list:
        get_files_url(url=url) 





