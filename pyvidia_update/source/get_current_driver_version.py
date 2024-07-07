import logging
import requests

from bs4 import BeautifulSoup as Bs


logger = logging.getLogger(__name__)

not_found_text = "Could not fetch current version for selected driver!"


def get_current_driver_version(url: str):
    try:
        response = requests.get(url)
        soup = Bs(response.text, features="html.parser")
        version_tag = soup.find(id="tdVersion")
        if not version_tag:
            return not_found_text
        current_version = version_tag.text
        if not current_version:
            return not_found_text
        return current_version.strip().replace("WHQL", "").strip()
    except Exception as e:
        logger.error(e)
        return "Could not fetch current version for selected driver!"
