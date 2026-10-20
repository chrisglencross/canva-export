import logging
import os
import subprocess
import tempfile
from pathlib import Path

import yaml

from .canva_auth import get_session
from .canva_api import download, get_updated_at

FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

logger = logging.getLogger('canva_export')

def transcode(input, output):
    ffmpeg = [
        "ffmpeg", "-y", "-nostdin",
        "-i", input,
        "-vcodec", "libx264",
        "-tune", "stillimage",
        "-movflags", "+faststart",
        "-crf", "31",
        "-filter:v", "fps=15",
        output
    ]
    return subprocess.run(ffmpeg).returncode

def upload(localfile, host, username, password, remotefile):
   logger.info(f"Uploading {localfile} to ftp://{host}/{remotefile}")
   curl = [
       "curl", "-s", "--ssl-reqd",
       "-u", f"{username}:{password}",
       "-T", localfile,
       f"ftp://{host}/{remotefile}"
   ]
   return subprocess.run(curl).returncode

def main():

    with open(".config.yaml", "r") as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)

    client_id=config["canva"]["client_id"]
    client_secret=config["canva"]["client_secret"]
    design_id = config["canva"]["design_id"]

    session = get_session(client_id, client_secret)
    updated_at = get_updated_at(session, design_id)

    if Path(".last_modified").exists():
        with open(".last_modified", "r") as last_modified_file:
            last_updated_at = last_modified_file.read()
    else:
        last_updated_at = None

    if last_updated_at and updated_at == last_updated_at:
        logger.info(f"Canva design not modified since {updated_at}")
        exit(16)

    logger.info(f"Downloading Canva design modified at {updated_at}")

    with tempfile.TemporaryDirectory() as tmpdir:
        download_file = f"{tmpdir}/download.mp4"
        transcoded_file = f"{tmpdir}/transcode.mp4"

        if not download(session, design_id, download_file):
            exit(1)
        logger.info(f"Downloaded {download_file}")

        logger.info(f"Transcoding to {transcoded_file}")
        return_code = transcode(download_file, transcoded_file)
        if return_code != 0:
            print(f"File transcode failed: {return_code}")
            exit(2)
        logger.info(f"Transcode reduced size from {os.path.getsize(download_file)//1024}KiB to {os.path.getsize(transcoded_file)//1024}KiB")

        return_code = upload(transcoded_file,
            config["ftp"]["hostname"],
            config["ftp"]["username"],
            config["ftp"]["password"],
            f"files/clubroom-video.mp4")
        if return_code != 0:
            print(f"File upload failed: {return_code}")
            exit(3)
        logger.info("File uploaded")

    with open(".last_modified", "w") as last_modified_file:
        last_modified_file.write(updated_at)

if __name__ == "__main__":
    main()
