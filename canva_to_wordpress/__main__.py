import logging
import os
import subprocess
import tempfile

import yaml

from .canva_auth import get_session
from .canva_api import download, get_updated_at
from .wordpress_client import WordPressClient

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
        output
    ]
    return subprocess.run(ffmpeg).returncode

def main():

    with open(".config.yaml", "r") as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)

    wordpress_client = WordPressClient(username=config["wordpress"]["username"], password=config["wordpress"]["password"])
    wordpress_slug = config["wordpress"]["slug"]
    media = wordpress_client.get_media(wordpress_slug)

    if media:
        media_id = media[0]["id"]
        media_description = media[0]["caption"]
        logger.info(f"Found item in WordPress: {media_description}")
    else:
        media_id, media_description = None, None
        logger.info("Media not found in WordPress")

    client_id=config["canva"]["client_id"]
    client_secret=config["canva"]["client_secret"]
    design_id = config["canva"]["design_id"]

    session = get_session(client_id, client_secret)
    updated_at = get_updated_at(session, design_id)

    expected_media_description = f"Updated at {updated_at}"

    if media_description and expected_media_description in media_description["rendered"]:
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
        # transcoded_file = download_file

        if media_id:
            wordpress_client.delete_media(media_id)
            logger.info(f"Deleted old media {media_id} with slug")

        logger.info(f"Uploading to {transcoded_file} to Wordpress")
        new_media = wordpress_client.upload_media(transcoded_file, f"{wordpress_slug}.mp4", "video/mp4")
        logger.info(f"Uploaded id={new_media['id']} to {new_media['link']}")

        wordpress_client.set_media_properties(new_media["id"], {
            "title": "Clubroom Video",
            "slug": wordpress_slug,
            "caption": expected_media_description,
        })


if __name__ == "__main__":
    main()
