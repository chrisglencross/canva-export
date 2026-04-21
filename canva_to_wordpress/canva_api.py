import logging
import time
from datetime import datetime, timezone

import requests
from canva_to_wordpress import canva_auth

logger = logging.getLogger('canva_api')

def get_updated_at(session: canva_auth.Session, design_id: str) -> str:
    response = requests.get(f"https://api.canva.com/rest/v1/designs/{design_id}",
                            headers={
                                "Authorization": f"Bearer {session.access_token}"
                            })
    response.raise_for_status()
    data = response.json()
    epoch = data["design"]["updated_at"]
    return datetime.fromtimestamp(epoch, timezone.utc).isoformat()

def start_export_job(session: canva_auth.Session, design_id: str):
    logger.info(f"Exporting design {design_id}...")
    response = requests.post("https://api.canva.com/rest/v1/exports",
                             headers={
                                 "Authorization": f"Bearer {session.access_token}",
                                 "Content-Type": "application/json"
                             },
                             json={
                                 "design_id": design_id,
                                 "format": {
                                     "type": "mp4",
                                     "quality": "horizontal_4k",  # or horizontal_1080p
                                     "export_quality": "pro", # or regular
                                 }
                             })
    response.raise_for_status()
    return response.json()["job"]

def poll_export_job(session: canva_auth.Session, job_id: str):
    response = requests.get(f"https://api.canva.com/rest/v1/exports/{job_id}",
                            headers={
                                "Authorization": f"Bearer {session.access_token}"
                            })
    response.raise_for_status()
    return response.json()["job"]

def download_file(url, target_file):
    logger.info(f"Downloading to {target_file}...")
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(target_file, "wb") as fp:
            for chunk in response.iter_content(chunk_size=8192):
                fp.write(chunk)

def download(session, design_id, target_file):
    job = start_export_job(session, design_id)
    while job["status"] == "in_progress":
        logger.info(f"Waiting for job {job["id"]}...")
        time.sleep(10)
        job = poll_export_job(session, job["id"])
    if job["status"] == "success":
        download_file(job["urls"][0], target_file)
        return True
    else:
        logger.error(f"Export job failed: {job}")
        return False
