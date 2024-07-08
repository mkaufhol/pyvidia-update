import logging
import os.path
import pickle
from pathlib import Path

from dataclasses import dataclass
from appdirs import user_data_dir

logger = logging.getLogger(__name__)


user_dir = user_data_dir("pyvidia-update-checker", "Maalik Kaufhold")


@dataclass
class SelectedDrivers:
    product_type: str | None
    product_series: str | None
    product: str | None
    os: str | None
    dt: str | None
    language: str | None
    dl_link: str | None

    _pickle_file: str = Path(user_dir).joinpath("saved_selected_config.pkl")

    def __init__(self):
        pass

    def to_dict(self):
        return {
            "product_type": self.product_type,
            "product_series": self.product_series,
            "product": self.product,
            "os": self.os,
            "dt": self.dt,
            "language": self.language,
            "dl_link": self.dl_link,
        }

    def _load_from_dict(self, data: dict):
        self.product_type = data.get("product_type", None)
        self.product_series = data.get("product_series", None)
        self.product = data.get("product", None)
        self.os = data.get("os", None)
        self.dt = data.get("dt", None)
        self.language = data.get("language", None)
        self.dl_link = data.get("dl_link", None)

    @staticmethod
    def _check_if_dir_exists():
        if not os.path.exists(user_dir):
            try:
                os.makedirs(user_dir)
            except OSError as e:
                logger.error(e)

    def save_as_pkl(self):
        self._check_if_dir_exists()
        with open(self._pickle_file, "wb+") as f:
            pickle.dump(self.to_dict(), f)

    def load_from_pkl(self):
        if not os.path.exists(self._pickle_file):
            data = {}
        else:
            with open(self._pickle_file, "rb") as f:
                data = pickle.load(f)
        self._load_from_dict(data)
