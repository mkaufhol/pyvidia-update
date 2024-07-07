import logging
import requests

from dataclasses import dataclass
from bs4 import BeautifulSoup as Bs


logger = logging.getLogger(__name__)


@dataclass
class CurrentDriverInfo:
    version: str
    release_date: str


driver_info = CurrentDriverInfo(
    version="Could not fetch current version for selected driver!",
    release_date="Not Found!",
)


def get_current_driver_version(url: str) -> CurrentDriverInfo:
    try:
        response = requests.get(url)
        soup = Bs(response.text, features="html.parser")

        version_tag = soup.find(id="tdVersion")
        if not version_tag:
            return driver_info

        current_version = version_tag.text
        if not current_version:
            return driver_info
        driver_info.version = current_version.strip().replace("WHQL", "").strip()

        release_date_tag = soup.find(id="tdReleaseDate")
        if not release_date_tag:
            return driver_info

        release_date = release_date_tag.text
        if not release_date:
            return driver_info
        driver_info.release_date = release_date.strip()

        return driver_info
    except Exception as e:
        logger.error(e)
        return driver_info
