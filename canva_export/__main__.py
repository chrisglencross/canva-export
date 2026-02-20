import argparse
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from .auth import get_session
from .canva_api import download, get_updated_at

FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

logger = logging.getLogger('canva_export')

def get_downloaded_timestamp(output):
    output_timestamp_file = Path(f"{output}.ts")
    if output_timestamp_file.is_file():
        return output_timestamp_file.read_text().strip()
    return None

def set_downloaded_timestamp(output, updated_at: str):
    output_timestamp_file = Path(f"{output}.ts")
    output_timestamp_file.write_text(updated_at)

def main():

    parser = argparse.ArgumentParser(description="Exports presentations from Canva")
    parser.add_argument("-d", "--design-id", help="Canva design id", required=True)
    parser.add_argument("-o", "--output", help="Target file", required=False)
    args = parser.parse_args()

    design_id = args.design_id
    output = args.output or f"{design_id}.mp4"

    load_dotenv()
    client_id=os.getenv("CANVA_CLIENT_ID")
    client_secret=os.getenv("CANVA_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("Set both CANVA_CLIENT_ID and CANVA_SECRET_ID in environment variables")
        exit(1)

    session = get_session(client_id, client_secret)
    updated_at = get_updated_at(session, design_id)

    if Path(output).is_file() and get_downloaded_timestamp(output) == updated_at:
        logger.info(f"Design not modified since {updated_at}")
        exit(16)

    logger.info(f"Downloading design modified at {updated_at}")
    if download(session, design_id, output):
        set_downloaded_timestamp(output, updated_at)
    logger.info(f"Downloaded {output}")

if __name__ == "__main__":
    main()