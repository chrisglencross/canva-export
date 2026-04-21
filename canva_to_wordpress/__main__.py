import logging
import tempfile

import yaml

from .canva_auth import get_session
from .canva_api import download, get_updated_at
from .wordpress_client import WordPressClient

FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

logger = logging.getLogger('canva_export')

def main():

    with open(".config.yaml", "r") as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)

    wordpress_client = WordPressClient(username=config["wordpress"]["username"], password=config["wordpress"]["password"])
    wordpress_slug = config["wordpress"]["slug"]
    media = wordpress_client.get_media(wordpress_slug)
    logger.info(f"Found {len(media)} items of media in WordPress")
    media_id = media[0]["id"] if media else None
    media_description = media[0]["caption"] if media else None

    client_id=config["canva"]["client_id"]
    client_secret=config["canva"]["client_secret"]
    design_id = config["canva"]["design_id"]

    session = get_session(client_id, client_secret)
    updated_at = get_updated_at(session, design_id)

    expected_media_description = f"Canva modified at {updated_at}"

    if media_description and expected_media_description in media_description["rendered"]:
        logger.info(f"Design not modified since {updated_at}")
        exit(16)

    logger.info(f"Downloading Canva design modified at {updated_at}")

    with tempfile.NamedTemporaryFile(mode='wb', delete=True, delete_on_close=False, suffix=".mp4") as fp:
        if download(session, design_id, fp):
            fp.close()
            logger.info(f"Downloaded {fp.name}")

            logger.info(f"Uploading to {wordpress_slug}.mp4 to Wordpress")
            new_media = wordpress_client.upload_media(media_id, fp.name, f"{wordpress_slug}.mp4", "video/mp4")
            logger.info(f"Uploaded id={new_media["id"]} to {new_media["link"]}")
            wordpress_client.set_media_properties(new_media["id"], {
                "title": "Clubroom Video",
                "slug": wordpress_slug,
                "caption": expected_media_description,
            })
        else:
            exit(1)


if __name__ == "__main__":
    main()