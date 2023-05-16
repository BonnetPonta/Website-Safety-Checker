import logging
import os
from time import time

import PySimpleGUI as sg
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def check_websiteSafety(url: str):
    """トレンドマイクロによるwebsite安全性評価"""
    start = time()
    logger.debug(f"トレンドマイクロによるwebsite安全性評価を行います: {url}")
    try:
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--incognito')
        options.add_argument('--disable-extensions')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.page_load_strategy = 'eager'
        options.add_argument('--log-level=3')
        logging.getLogger("WDM").setLevel(logging.ERROR)

        logger.debug("selenium driverを起動します")

        driver = Chrome(service=fs.Service(ChromeDriverManager().install()), options=options)
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        if driver is None:
            raise Exception("driver is None.")
        driver.get("https://global.sitesafety.trendmicro.com/?cc=jp")
        txt_box = driver.find_element(By.ID, "urlname")
        txt_box.send_keys(url)
        txt_box.submit()
        bannerholder = driver.find_element(By.CLASS_NAME, "bannerholder")

        html = bannerholder.get_attribute("innerHTML")
        if html is None:
            raise Exception("html is none.")
        soup = BeautifulSoup(html, "html.parser")
        if soup is None:
            raise Exception("soup is none.")

        status = soup.select_one(".labeltitleresult").text
        categories = ", ".join([category.text for category in soup.select(".labeltitlesmallresult")])
        logger.info(f"""
                    トレンドマイクロによるwebsite安全性
                    status: {status}
                    categories: {categories}
                    """)
        return status, categories
    except Exception as e:
        logger.error(e, f"selenium driver. url: {url}")
        return None, None
    finally:
        try:
            driver.quit()
            logger.debug(f"seleniumにかかった時間: {time()-start}")
        except Exception as e:
            logger.error(f"seleniumのブラウザを閉じるのに失敗しました。: {e}")


def main():
    layout = [
        [sg.Text("URLを入力してください:")],
        [sg.Input(key="-URL-")],
        [sg.Button("チェック"), sg.Button("終了")],
        [sg.Text("status: ", size=(40, 1), key="-STATUS-")],
        [sg.Text("categories: ", size=(40, 5), key="-CATEGORIES-")],
    ]

    window = sg.Window("Website安全性チェック", layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "終了":
            break

        if event == "チェック":
            url = values["-URL-"]
            status, categories = check_websiteSafety(url)

            window["-STATUS-"].update(f"status: {status}")
            window["-CATEGORIES-"].update(f"categories: {categories}")

    window.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(os.path.basename(__file__))
    logger.info("start")
    main()
    logger.info("end")
