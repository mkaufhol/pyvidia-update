import asyncio
import os
import random
import pickle
from dataclasses import dataclass

import cmd
import json
from enum import Enum
from itertools import islice

import aiohttp

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

"""
json format:
{
    <product_type_id>: {
        verbose_name: <str>,
        <product_series_id>: {
            verbose_name: <str>,
            <product_id>: {
                verbose_name: <str>,
                <operating_system_id>: {
                    verbose_name: <str>,
                    <download_type_id>: {
                        verbose_name: <str>,
                        <language_id>: <str>,
                    },
                    ...
                },
                ...
            },
            ...
        },
        ...
    },
    ...
}

Product Type:   1       dtcid
Product Series: 127     psid
Product:        1041    pfid
OS:             135     osid
Download Type:  18      dtid
Language:       9       lid

https://www.nvidia.com/Download/processDriver.aspx?
psid=127&pfid=1041&rpf=1&osid=135&lid=9&lang=en-us&ctk=0&dtid=18&dtcid=1

request list format:
[
    {
        dtcid: <int>,
        psid: <int>,
        pfid: <int>,
        osid: <int>,
        dtid: <int>,
        lid: <int>,
    },
    ...
]
"""


@dataclass
class OptionDict:
    element: WebElement
    data: dict


@dataclass
class NvidiaUrlLookupParameter:
    dtcid: int | str | None = None
    psid: int | str | None = None
    pfid: int | str | None = None
    osid: int | str | None = None
    dtid: int | str | None = None
    lid: int | str | None = None

    def to_url_params(self) -> str:
        return f"?dtcid={self.dtcid}&psid={self.psid}&pfid={self.pfid}&osid={self.osid}&dtid={self.dtid}&lid={self.lid}"


class WebDriverSelection(Enum):
    CHROME: webdriver.Chrome = webdriver.Chrome
    FIREFOX: webdriver.Firefox = webdriver.Firefox


class NvidiaDriverScraper(cmd.Cmd):
    prompt = ">> "
    intro = "Nvidia Driver Download page scraper. Type 'help' for available commands."

    _selected_driver: WebDriverSelection = WebDriverSelection.CHROME
    driver: webdriver.Chrome | webdriver.Firefox | None = None

    _base_url: str = "https://www.nvidia.com/Download/processDriver.aspx"
    json_output: dict = {}

    _consumer_types = ["geforce", "titan", "quadro"]

    # TODO: Replace this with a real argument parser
    json_file_path = "./data/nvidia-dropdown-values.json"
    pickle_file_path = ""
    skip_languages = True
    os_limit = "windows"
    use_json = True
    only_consumer_types = True

    def __init__(self):
        super().__init__()
        self.pickle_file_path = self.json_file_path.replace(".json", ".pkl")

    def precmd(self, line):
        return line

    def do_init(self, arg: str):
        """
        Initialize the scraper. You can either choose the default initialization by passing
        no argument or customize the scraper by passing 'chrome' or 'firefox' argument.

        Default would initialize:
          - Chrome webdriver
          - english as selected language
          - only the Windows driver
          - Get data from the json_file_path if exist instead of calling the website

        init <chrome|firefox> <en|all> <windows|all> <online|cache>

        Note: To fetch the list of all languages it would take quite some time for the
        selenium driver to select all, so please stick to en only if you want to save time.
        """
        args = arg.split(" ")
        if len(args) > 0 and args[0] == "firefox":
            self._selected_driver = WebDriverSelection.FIREFOX
            print("Selected Firefox webdriver")
        else:
            self._selected_driver = WebDriverSelection.CHROME
            print("Selected Chrome webdriver")
        if len(args) > 1 and args[1] == "all":
            self.skip_languages = False
            print("Get all language drivers")
        else:
            self.skip_languages = True
            print("Only get the english drivers")
        if len(args) > 2 and args[2] == "all":
            self.os_limit = "all"
            print("Get all os drivers")
        else:
            self.os_limit = "windows"
            print("Only get the windows drivers")
        if len(args) > 3 and args[3] == "online":
            self.use_json = False
            print("Get new JSON from Nvidia page")
        else:
            self.use_json = True
            print("Use existing JSON")
        if len(args) > 4 and args[4] == "no":
            self.only_consumer_types = False
            print("Get all Product Types")
        else:
            self.only_consumer_types = True
            print("Get only consumer Product Types")

    def do_open_driver(self, arg):
        self._init_driver()

    # TODO: Add better documentation and some options
    def do_scrape(self, arg):
        """
        Start the scraping process.

        :param arg:
        :return:
        """
        self.scrape_drivers()

    def do_cleanup(self, arg):
        self.cleanup_json()

    def do_compress(self, arg):
        self.store_compressed()

    def do_quit(self, line):
        """Exit the program."""
        self._exit_tasks()
        return True

    def do_exit(self, line):
        """Exit the program."""
        self._exit_tasks()
        return True

    def postcmd(self, stop, line):
        print()
        return stop

    def _exit_tasks(self):
        if self.driver is not None and isinstance(
            self.driver, (webdriver.Chrome, webdriver.Firefox)
        ):
            print("Stopping webdriver")
            self.driver.quit()
            self.driver = None

    def _init_driver(self):
        self.driver = self._selected_driver.value()

    def _get_option_dict(self, element_id: str) -> OptionDict:
        element: WebElement = self.driver.find_element(By.ID, element_id)
        data: dict = {
            opt.get_property("value"): opt.text
            for opt in element.find_elements(By.TAG_NAME, "option")
        }
        return OptionDict(element=element, data=data)

    @staticmethod
    def _select_option(element: WebElement, value: str, by_name: bool = False):
        try:
            select = Select(element)
            if by_name:
                select.select_by_visible_text(value)
                return True
            select.select_by_value(value)
            return True
        except Exception:
            return False

    @staticmethod
    async def _random_wait(chunk_num, total_chunks):
        min_wait = 1  # minimum seconds to wait
        max_wait = 7  # maximum seconds to wait
        wait_time = random.randint(min_wait, max_wait)
        print(
            f"({chunk_num}/{total_chunks}) Randomly waiting for {wait_time} seconds before sending chunk"
        )
        await asyncio.sleep(wait_time)

    @staticmethod
    def _chunk_iterable(iterable, chunk_size: int = 20):
        it = iter(iterable)
        while True:
            chunk = list(islice(it, chunk_size))
            if not chunk:
                break
            yield chunk

    async def _get_download_urls_of_chunk(
        self,
        params_list: list[NvidiaUrlLookupParameter],
        session: aiohttp.ClientSession,
    ):
        tasks = []

        for param in params_list:
            task = asyncio.ensure_future(self._add_download_url(param, session=session))
            tasks.append(task)

        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _add_download_url(
        self, param: NvidiaUrlLookupParameter, session: aiohttp.ClientSession
    ):
        timeout = 10
        url = f"{self._base_url}{param.to_url_params()}"
        try:
            async with session.get(url, timeout=timeout) as response:
                result = await response.text()
                if "No certified downloads" in result or "DOCTYPE html" in result:
                    print(f"No download found for {url}")
                    download_url = "not_found"
                elif "Access Denied" in result:
                    print(f"Access Denied for {url}")
                    download_url = "access_denied"
                elif "nvidia" not in result:
                    download_url = f"https://www.nvidia.com/Download/{result}"
                else:
                    download_url = f"https:{result}"
                self.json_output[param.dtcid][param.psid][param.pfid][param.osid][
                    param.dtid
                ][param.lid]["download_url"] = download_url
                print(f"Received {download_url}")
        except Exception as e:
            print(f"Fetching of {url} failed. Error message: {e}")

    async def _fetch_urls(self, url_lookup: list[NvidiaUrlLookupParameter]):
        print(f"Fetched {len(url_lookup)} driver selections, running URL fetcher now")
        self._exit_tasks()

        max_workers = 20

        tcp_conn = aiohttp.TCPConnector(limit=max_workers)
        async with aiohttp.ClientSession(connector=tcp_conn) as session:
            for i, url_lookup_chunk in enumerate(
                self._chunk_iterable(url_lookup, max_workers)
            ):
                await self._random_wait(i, (len(url_lookup) // max_workers))
                await self._get_download_urls_of_chunk(url_lookup_chunk, session)

        await tcp_conn.close()

        with open(self.pickle_file_path, "wb+") as f:
            print(f"Dumping JSON with download URLs to {self.json_file_path}")
            pickle.dump(self.json_output, f)

    def scrape_drivers(self):
        if self.use_json and os.path.exists(self.json_file_path):
            with open(self.pickle_file_path, "rb") as f:
                self.pickle_file_path: dict = pickle.load(f)
            url_lookup: list[NvidiaUrlLookupParameter] = []

            for ptk, ptv in self.json_output.items():
                for psk, psv in ptv.items():
                    if psk == "verbose_name":
                        continue
                    for pk, pv in psv.items():
                        if pk == "verbose_name":
                            continue
                        for osk, osv in pv.items():
                            if osk == "verbose_name":
                                continue
                            for dtk, dtv in osv.items():
                                if dtk == "verbose_name":
                                    continue
                                for lgk in dtv.keys():
                                    if lgk == "verbose_name":
                                        continue
                                    url_lookup.append(
                                        NvidiaUrlLookupParameter(
                                            dtcid=ptk,
                                            psid=psk,
                                            pfid=pk,
                                            osid=osk,
                                            dtid=dtk,
                                            lid=lgk,
                                        )
                                    )

            asyncio.run(self._fetch_urls(url_lookup))
            return

        self._init_driver()
        self.driver.get("https://www.nvidia.com/Download/index.aspx")

        product_type = self._get_option_dict("selProductSeriesType")

        url_lookup: list[NvidiaUrlLookupParameter] = []

        for pt_value, pt_name in product_type.data.items():
            if not any([s in pt_name.lower() for s in self._consumer_types]):
                continue
            check = self._select_option(product_type.element, pt_value)
            if not check:
                continue
            self.json_output[pt_value] = {"verbose_name": pt_name}
            product_series = self._get_option_dict("selProductSeries")

            for ps_value, ps_name in product_series.data.items():
                check = self._select_option(product_series.element, ps_value)
                if not check:
                    continue
                self.json_output[pt_value][ps_value] = {"verbose_name": ps_name}
                product = self._get_option_dict("selProductFamily")

                for p_value, p_name in product.data.items():
                    check = self._select_option(product.element, p_value)
                    if not check:
                        continue
                    self.json_output[pt_value][ps_value][p_value] = {
                        "verbose_name": p_name
                    }
                    operating_system = self._get_option_dict("selOperatingSystem")

                    for os_value, os_name in operating_system.data.items():
                        if (
                            self.os_limit == "windows"
                            and "windows" not in os_name.lower()
                        ):
                            continue
                        check = self._select_option(operating_system.element, os_value)
                        if not check:
                            continue
                        self.json_output[pt_value][ps_value][p_value][os_value] = {
                            "verbose_name": os_name
                        }
                        download_type = self._get_option_dict("ddlDownloadTypeCrdGrd")

                        for dt_value, dt_name in download_type.data.items():
                            check = self._select_option(download_type.element, dt_value)
                            if not check:
                                continue
                            self.json_output[pt_value][ps_value][p_value][os_value][
                                dt_value
                            ] = {"verbose_name": dt_name}
                            language = self._get_option_dict("ddlLanguage")

                            if self.skip_languages:
                                english_string = "English (US)"
                                english_value = next(
                                    k
                                    for k, val in language.data.items()
                                    if val == english_string
                                )
                                check = self._select_option(
                                    language.element, english_string, by_name=True
                                )
                                if not check:
                                    continue
                                if not english_value:
                                    print(
                                        f"Value {english_value} not in Language Dropdown!"
                                    )
                                    continue
                                self.json_output[pt_value][ps_value][p_value][os_value][
                                    dt_value
                                ][english_value] = {"verbose_name": english_string}
                                url_lookup.append(
                                    NvidiaUrlLookupParameter(
                                        dtcid=pt_value,
                                        psid=ps_value,
                                        pfid=p_value,
                                        osid=os_value,
                                        dtid=dt_value,
                                        lid=english_value,
                                    )
                                )
                                continue
                            for lg_value, lg_name in language.data.items():
                                check = self._select_option(language.element, lg_value)
                                if not check:
                                    continue
                                self.json_output[pt_value][ps_value][p_value][os_value][
                                    dt_value
                                ][lg_value] = {"verbose_name": lg_name}
                                url_lookup.append(
                                    NvidiaUrlLookupParameter(
                                        dtcid=pt_value,
                                        psid=ps_value,
                                        pfid=p_value,
                                        osid=os_value,
                                        dtid=dt_value,
                                        lid=lg_value,
                                    )
                                )
            #                     break  # Language
            #                 break  # Download Type
            #             break  # OS
            #         break  # Product
            #     break  # Product Series
            # break  # Product Type

        with open(self.pickle_file_path, "wb+") as f:
            print(f"Dumping JSON to {self.pickle_file_path}")
            pickle.dump(self.json_output, f)

        asyncio.run(self._fetch_urls(url_lookup))

    def cleanup_json(self):
        if not os.path.exists(self.pickle_file_path):
            print(f"File {self.pickle_file_path} not found!")
            return

        with open(self.pickle_file_path, "rb") as f:
            self.json_output: dict = pickle.load(f)

        url_lookup: list[NvidiaUrlLookupParameter] = []

        for ptk, ptv in self.json_output.items():
            for psk, psv in ptv.items():
                if psk == "verbose_name":
                    continue
                for pk, pv in psv.items():
                    if pk == "verbose_name":
                        continue
                    for osk, osv in pv.items():
                        if osk == "verbose_name":
                            continue
                        for dtk, dtv in osv.items():
                            if dtk == "verbose_name":
                                continue
                            for lgk, lgv in dtv.items():
                                if lgk == "verbose_name":
                                    continue
                                lookup = NvidiaUrlLookupParameter(
                                    dtcid=ptk,
                                    psid=psk,
                                    pfid=pk,
                                    osid=osk,
                                    dtid=dtk,
                                    lid=lgk,
                                )
                                download_url = lgv.get("download_url", "")
                                if "No certified downloads" in download_url:
                                    self.json_output[ptk][psk][pk][osk][dtk][lgk][
                                        "download_url"
                                    ] = "not_found"
                                elif (
                                    download_url == "access_denied"
                                    or "Access Denied" in download_url
                                    or "DOCTYPE html" in download_url
                                ):
                                    url_lookup.append(lookup)

        if len(url_lookup) > 0:
            asyncio.run(self._fetch_urls(url_lookup))

        with open(self.pickle_file_path, "wb+") as f:
            print(f"Dumping JSON to {self.pickle_file_path}")
            pickle.dump(self.json_output, f)

    def store_compressed(self):
        if not os.path.exists(self.json_file_path):
            print(f"File {self.json_file_path} not found!")
            return

        with open(self.json_file_path, "r") as f:
            data = json.load(f)

        if not data:
            return

        with open(self.pickle_file_path, "wb") as f:
            pickle.dump(data, f)
            print(f"Stored {self.json_file_path} as {self.pickle_file_path}")


if __name__ == "__main__":
    NvidiaDriverScraper().cmdloop()
