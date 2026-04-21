import logging
import requests
from requests.auth import HTTPBasicAuth

class WordPressClient:

    logger = logging.getLogger('WordPressClient')

    def __init__(self, username, password):
        self.hostname = "www.epsomandewellharriers.org"
        self.auth = HTTPBasicAuth(username, password)

    def get_media(self, slug):
        page=1
        media=[]
        while True:
            response = requests.get(f"https://{self.hostname}/wp-json/wp/v2/media/",
                                    params=f"per_page=100&page={page}&slug={slug}",
                                    auth=self.auth,
                                    headers={
                                        "Accept": "application/json",
                                        "User-Agent": "SyncFromSpond"
                                    })
            response.raise_for_status()
            media.extend(response.json())
            if page >= int(response.headers['X-WP-TotalPages']) or page > 10:
                break
            page += 1
        return media

    def upload_media(self, media_id, local_file, file_name, content_type):
        with open(local_file, 'rb') as f:
            response = requests.post(f"https://{self.hostname}/wp-json/wp/v2/media/{media_id or ""}",
                                     auth=self.auth,
                                     headers={
                                         "Accept": "application/json",
                                         "User-Agent": "SyncFromCanva",
                                         "Content-Type": content_type,
                                         "Content-Disposition": f'form-data; filename="{file_name}"'
                                     },
                                     data=f,
                                     stream=True
            )
            response.raise_for_status()
            return response.json()

    def set_media_properties(self, media_id, properties):
        response = requests.post(f"https://{self.hostname}/wp-json/wp/v2/media/{media_id}",
                                 auth=self.auth,
                                 headers={
                                     "Accept": "application/json",
                                     "User-Agent": "SyncFromCanva"
                                 },
                                 json=properties
                                 )
        response.raise_for_status()
