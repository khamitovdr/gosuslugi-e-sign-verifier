import os
import re
from time import sleep
from typing import Any

from xvfbwrapper import Xvfb
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def select_region(wait: WebDriverWait) -> None:
    """
    Select region
    """
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # region_auto_select = wait.until(
    #     EC.presence_of_element_located((By.CLASS_NAME, "region-auto-search-block"))
    # )
    # region_auto_select.click()

    region_select = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@label='Выбрать вручную']")))
    region_select.click()

    region_input = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@type='search']")))
    region_input.send_keys("Москва")

    msk = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='dropdown-el']//li")))
    msk.click()

    save_button = wait.until(EC.presence_of_element_located((By.XPATH, "//*[text()='Сохранить']")))
    save_button.click()


def upload_files(file_path: str, sig_path: str, driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    """
    Upload files
    """
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
    sleep(1)
    file_upload_input, signature_input = driver.find_elements(By.XPATH, "//input[@type='file']")
    file_upload_input.send_keys(file_path)
    print("File uploaded")

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "loaded")))
    sleep(3)

    signature_input.send_keys(sig_path)
    print("Sig uploaded")

    try:
        check_button = wait.until(EC.presence_of_element_located((By.XPATH, "//a[text()='Проверить']")))
    except TimeoutException:
        raise ValueError("Signature file format is not valid")
    
    driver.execute_script("arguments[0].scrollIntoView();", check_button)
    check_button = driver.find_element(By.XPATH, "//a[text()='Проверить']")
    check_button.click()
    print("Check clicked")


def get_check_result(wait: WebDriverWait) -> bool:
    """
    Get check result
    """
    result = wait.until(
        EC.presence_of_element_located((By.XPATH, "//span[@ng-bind='steps.stepTwo.result.message.title']"))
    )
    return result.text == "Электронная подпись действительна"


def get_check_report(wait: WebDriverWait) -> dict[str, Any]:
    """
    Get check report
    """
    report_status = wait.until(EC.presence_of_element_located((By.XPATH, "//*[text()='Статус подписи']")))
    report = report_status.find_element(By.XPATH, "../..")

    report_info = {}
    for row in report.find_elements(By.XPATH, "./*"):
        key, val = row.find_elements(By.XPATH, "./*")
        report_info[key.text] = val.text

    try:
        certificate_info = {}
        for key, val, _ in re.findall(r"([A-ZА-Я]+)=(.+?)((?<!\\)(?:\\\\)*,|$)", report_info["Владелец сертификата"]):
            certificate_info[key] = val.replace("\\", "")

        report_info["certificate_info"] = certificate_info
    except Exception:
        pass

    return report_info


class GosUslugi:
    """
    GosUslugi class
    """
    GOSUSLUGI_URL = os.getenv("GOSUSLUGI_URL")

    def __init__(self):
        self.xvfb = Xvfb(width=1920, height=1080)
        self.xvfb.start()
        print("Xvfb screen emulator started")

        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options)
        print("Chrome driver started")
        self.refresh()

        self.wait = WebDriverWait(self.driver, 30)
        select_region(self.wait)

    def refresh(self):
        """
        Refresh page
        """
        self.driver.get(self.GOSUSLUGI_URL)
        print("Page refreshed")

    def check_signature(self, file_path: str, sig_path: str) -> tuple[bool, dict]:
        """
        Check signature
        """
        upload_files(file_path, sig_path, self.driver, self.wait)
        result = get_check_result(self.wait)
        report = get_check_report(self.wait)
        self.refresh()

        return result, report

    def __del__(self):
        self.xvfb.stop()
        self.driver.quit()
