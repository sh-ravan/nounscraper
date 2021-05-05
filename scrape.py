import os
import re
import sys
import time
from base64 import b64decode as base64_decode
from html import unescape
from unicodedata import normalize
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
# options.add_argument('--headless')
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)


def scroll_down(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # <--- slow internet connection? increase this number (seconds)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def get_page_content(url, icon_page=False):
    driver.get(url)
    if icon_page:
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".iconPreview")))
    else:
        scroll_down(driver)
    content = driver.page_source
    return content


def scrape_index(index_url):
    contents = get_page_content(index_url)
    soup = BeautifulSoup(contents, features="html.parser")
    links = soup.find_all("a")
    urls = set()
    for link in links:
        url = link.get("href")
        if "/term/" in url:
            urls.add(urljoin(index_url, url))
    return list(urls)


def scrape_icon(url):
    contents = get_page_content(url, icon_page=True)
    soup = BeautifulSoup(contents, features="html.parser")
    noun = soup.find("h1", attrs={"class": "main-term"}).text
    icon = soup.find("div", attrs={"class": "iconPreview"})
    noun_url = soup.find("link", attrs={"rel": "canonical"}).get("href")
    noun_id = None
    match = re.search(r"/(\d+)/", noun_url)
    if match:
        noun_id = match.group(1)
    designer = soup.find("div", attrs={"class": "designer"}).text
    license_str = soup.find("div", attrs={"class": "license-strip"}).text
    attribution_text = (
        noun.strip() + " by " + designer.strip() + " from the Noun Project"
    )
    attribution_text = normalize("NFKD", attribution_text)
    style_string = unescape(icon.get("style"))
    style_string = style_string.split("data:image/svg+xml;base64,")[1]
    svg_string = style_string.split('");')[0]
    base64_bytes = svg_string.encode("ascii")
    svg_string = base64_decode(base64_bytes).decode("ascii")
    svg_string = re.sub("height='\d+px'", "", svg_string)
    svg_string = re.sub("width='\d+px'", "", svg_string)

    return {
        "id": noun_id,
        "svg": svg_string,
        "license": license_str,
        "attr_text": attribution_text,
    }


def store_icon(icon_data):
    out = os.path.join(os.path.dirname(__file__), "icons")
    try:
        os.makedirs(out)
    except OSError:
        pass
    filename = ""
    if icon_data["id"]:
        filename = icon_data["id"].strip() + "--" + icon_data["attr_text"]
    basename = os.path.join(out, filename)
    with open(basename + ".svg", "w") as fh:
        fh.write('<?xml version="1.0" encoding="utf-8"?>\n'
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">\n')
        fh.write(icon_data["svg"])
        with open(basename + ".json", "w") as fh:
            fh.write(f"ID: {icon_data['id']}\n"
                     f"Local Filename: {basename}.svg\n"
                     f"License: {icon_data['license']}\n"
                     f"Attribution Text: {icon_data['attr_text']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scrape.py <nounproject url> [<more urls>...]")
        print(
            "Example: python scrape.py http://thenounproject.com/collections/modern-pictograms/"
        )
        sys.exit(1)
    for index_url in sys.argv[1:]:
        index_url = sys.argv[1]
        icon_urls = scrape_index(index_url)
        for url in icon_urls:
            try:
                icon_data = scrape_icon(url)
                store_icon(icon_data)
            except:
                print("Something went wrong while scraping " + url)
