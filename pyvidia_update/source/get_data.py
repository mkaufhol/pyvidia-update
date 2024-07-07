import logging
import os
import pickle

from pyvidia_update.source.get_files import get_packaged_files_path

logger = logging.getLogger(__name__)


filepath = get_packaged_files_path()


class DropdownData:
    pickle_data_path: str = f"{filepath}/data/nvidia-dropdown-values.pkl"
    data: dict = {}
    switch_kv: bool = False

    def __init__(self, switch_kv: bool = False):
        self.data = self._load_data()
        self.switch_kv = switch_kv

    def _load_data(self):
        if not os.path.exists(self.pickle_data_path):
            logger.error(f"Path {self.pickle_data_path} does not exist")
            raise FileNotFoundError(
                f"Path {self.pickle_data_path} does not exist."
                f"\nCurrent Path: {os.curdir} \n"
                f"|_ {'\n|_ '.join(os.listdir('.'))}"
            )
        with open(self.pickle_data_path, "rb") as f:
            data: dict = pickle.load(f)
            logger.debug(f"Loading data from file {self.pickle_data_path}")
            if not data:
                logger.warning(
                    f"File {self.pickle_data_path} does not contain any data"
                )
                return {}
        return data

    def _switch_key_values(self, data: dict):
        if self.switch_kv is False:
            return data
        return {v: k for k, v in data.items()}

    def get_product_type_data(self):
        return self._switch_key_values(
            {k: v.get("verbose_name", "") for k, v in self.data.items()}
        )

    def get_product_series_data(self, product_type_id: str):
        if product_type_id not in self.data.keys():
            raise ValueError(f"Key {product_type_id} does not exist in data!")
        return self._switch_key_values(
            {
                k: v.get("verbose_name", "")
                for k, v in self.data[product_type_id].items()
                if k != "verbose_name"
            }
        )

    def get_product_data(self, product_type_id: str, product_series_id: str):
        if (
            product_type_id not in self.data.keys()
            or product_series_id not in self.data[product_type_id].keys()
        ):
            raise ValueError(
                f"Key combination {product_type_id}, {product_series_id} does not exist in data!"
            )
        return self._switch_key_values(
            {
                k: v.get("verbose_name", "")
                for k, v in self.data[product_type_id][product_series_id].items()
                if k != "verbose_name"
            }
        )

    def get_os_data(
        self, product_type_id: str, product_series_id: str, product_id: str
    ):
        if (
            product_type_id not in self.data.keys()
            or product_series_id not in self.data[product_type_id].keys()
            or product_id not in self.data[product_type_id][product_series_id].keys()
        ):
            raise ValueError(
                f"Key combination {product_type_id}, {product_series_id}, {product_id} does not exist in data!"
            )
        return self._switch_key_values(
            {
                k: v.get("verbose_name", "")
                for k, v in self.data[product_type_id][product_series_id][
                    product_id
                ].items()
                if k != "verbose_name"
            }
        )

    def get_dt_data(
        self, product_type_id: str, product_series_id: str, product_id: str, os_id: str
    ):
        if (
            product_type_id not in self.data.keys()
            or product_series_id not in self.data[product_type_id].keys()
            or product_id not in self.data[product_type_id][product_series_id].keys()
            or os_id
            not in self.data[product_type_id][product_series_id][product_id].keys()
        ):
            raise ValueError(
                f"Key combination {product_type_id}, {product_series_id}, {product_id}, {os_id} does not exist in data!"
            )
        return self._switch_key_values(
            {
                k: v.get("verbose_name", "")
                for k, v in self.data[product_type_id][product_series_id][product_id][
                    os_id
                ].items()
                if k != "verbose_name"
            }
        )

    def get_language_data(
        self,
        product_type_id: str,
        product_series_id: str,
        product_id: str,
        os_id: str,
        dt_id: str,
    ):
        if (
            product_type_id not in self.data.keys()
            or product_series_id not in self.data[product_type_id].keys()
            or product_id not in self.data[product_type_id][product_series_id].keys()
            or os_id
            not in self.data[product_type_id][product_series_id][product_id].keys()
            or dt_id
            not in self.data[product_type_id][product_series_id][product_id][
                os_id
            ].keys()
        ):
            raise ValueError(
                f"Key combination {product_type_id}, {product_series_id}, {product_id}, {os_id}, {dt_id} does not exist in data!"
            )
        return self._switch_key_values(
            {
                k: v.get("verbose_name", "")
                for k, v in self.data[product_type_id][product_series_id][product_id][
                    os_id
                ][dt_id].items()
                if k != "verbose_name"
            }
        )

    def get_download_link(
        self,
        product_type_id: str,
        product_series_id: str,
        product_id: str,
        os_id: str,
        dt_id: str,
        language_id: str,
    ) -> str:
        if (
            product_type_id not in self.data.keys()
            or product_series_id not in self.data[product_type_id].keys()
            or product_id not in self.data[product_type_id][product_series_id].keys()
            or os_id
            not in self.data[product_type_id][product_series_id][product_id].keys()
            or dt_id
            not in self.data[product_type_id][product_series_id][product_id][
                os_id
            ].keys()
            or language_id
            not in self.data[product_type_id][product_series_id][product_id][os_id][
                language_id
            ].keys()
        ):
            logger.error(
                f"Key combination {product_type_id}, {product_series_id}, {product_id}, {os_id}, {dt_id}, {language_id} does not exist in data!"
            )
            return ""
        return self.data[product_type_id][product_series_id][product_id][os_id][dt_id][
            language_id
        ].get("download_url", "not_found")
