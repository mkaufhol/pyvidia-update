import os
from dataclasses import dataclass

from dotenv import load_dotenv

import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

load_dotenv()

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
                    }
                }
            }
        }
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
    dtcid: int | str
    psid: int | str
    pfid: int | str
    osid: int | str
    dtid: int | str
    lid: int | str

    def to_url_params(self):
        return f"?dtcid={self.dtcid}&psid={self.psid}&pfid={self.pfid}&osid={self.osid}&dtid={self.dtid}&lid={self.lid}"


def get_option_dict(_driver: WebDriver, element_id: str) -> OptionDict:
    element: WebElement = _driver.find_element(By.ID, element_id)
    data: dict = {
        opt.get_property("value"): opt.text
        for opt in element.find_elements(By.TAG_NAME, "option")
    }
    return OptionDict(element=element, data=data)


def select_option(element: WebElement, value: str):
    try:
        select = Select(element)
        select.select_by_value(value)
        return True
    except NotImplementedError:
        return False


DRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH")

driver = webdriver.Chrome()

driver.get("https://www.nvidia.com/Download/index.aspx")

product_type = get_option_dict(driver, "selProductSeriesType")

json_output: dict = {}
url_lookup: list[NvidiaUrlLookupParameter] = []
try:
    for pt_value, pt_name in product_type.data.items():
        check = select_option(product_type.element, pt_value)
        if not check:
            continue
        json_output[pt_value] = {"verbose_name": pt_name}
        product_series = get_option_dict(driver, "selProductSeries")

        for ps_value, ps_name in product_series.data.items():
            check = select_option(product_series.element, ps_value)
            if not check:
                continue
            json_output[pt_value][ps_value] = {"verbose_name": ps_name}
            product = get_option_dict(driver, "selProductFamily")

            for p_value, p_name in product.data.items():
                check = select_option(product.element, p_value)
                if not check:
                    continue
                json_output[pt_value][ps_value][p_value] = {"verbose_name": p_name}
                operating_system = get_option_dict(driver, "selOperatingSystem")

                for os_value, os_name in operating_system.data.items():
                    check = select_option(operating_system.element, os_value)
                    if not check:
                        continue
                    json_output[pt_value][ps_value][p_value][os_value] = {
                        "verbose_name": os_name
                    }
                    download_type = get_option_dict(driver, "ddlDownloadTypeCrdGrd")

                    for dt_value, dt_name in download_type.data.items():
                        check = select_option(download_type.element, dt_value)
                        if not check:
                            continue
                        json_output[pt_value][ps_value][p_value][os_value][dt_value] = {
                            "verbose_name": dt_name
                        }
                        language = get_option_dict(driver, "ddlLanguage")

                        for lg_value, lg_name in language.data.items():
                            check = select_option(language.element, lg_value)
                            if not check:
                                continue
                            json_output[pt_value][ps_value][p_value][os_value][
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
except Exception as e:
    print(e)
finally:
    print(json_output)
    print(url_lookup)
    driver.quit()

for params in url_lookup:
    try:
        response = requests.get(
            f"https://www.nvidia.com/Download/processDriver.aspx{params.to_url_params()}"
        )
        if "nvidia" not in response.text:
            download_url = f"https://www.nvidia.com/Download/{response.text}"
        else:
            download_url = f"https:{response.text}"
        print(download_url)
        json_output[params.dtcid][params.psid][params.pfid][params.osid][params.dtid][
            params.lid
        ]["download_url"] = download_url
    except Exception as e:
        print(e)
