import re
import os
import requests
import datetime
import openpyxl
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    user_agent = UserAgent()

    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={user_agent.random}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    return webdriver.Chrome(options=options)


def scraper(driver, link_to_the_product=None):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    product_code = soup.find("div", class_="detailSection-item detailSection-productCode").text
    pattern = r"\s(\d+)"
    result = re.search(pattern, product_code)
    sku = int(result.group(1))

    breadcrumb = soup.find("ol", class_="breadcrumb")
    items = [item.text.strip() for item in breadcrumb.find_all("li")]
    str_category = "/".join(items)
    split_line = str_category.split("/")
    category_1 = split_line[1] if len(split_line) > 1 else "-"
    category_2 = split_line[2] if len(split_line) > 2 else "-"
    category_3 = split_line[3] if len(split_line) > 3 else "-"
    product_name = split_line[-1] if len(split_line) > 0 else "-"
    if category_2 == product_name and category_3 == "-":
        category_2 = "-"

    color = soup.find("label", class_="colorValue").text.strip()

    details = soup.find("span", class_="morecontent").text.strip().replace('\n', ' ')

    details = re.sub(r'Product code \d+', '', details)
    details = re.sub(r'Read More \+', '', details)

    details = details.replace('\n', ' ')

    details = re.sub(r'\s\s+', ' ', details)

    content_block = soup.find("div", class_="pdpContent-Desktop")
    img_tags = content_block.find_all('img')
    all_srcset_urls = []
    for img in img_tags:
        if img.get('srcset'):
            srcset = img['srcset']
            img_urls = [url.strip() for url in srcset.split(',') if '640w' in url]
            all_srcset_urls.extend(img_urls)

    unique_srcset_urls = list(set(all_srcset_urls))

    regex = r"/i/drmartens/[\w\d]+\.\d+"
    base_url = "https://i1.adis.ws"
    corrected_urls = []

    for url in unique_srcset_urls:
        match = re.search(regex, url)
        if match:
            corrected_urls.append(base_url + match.group() + ".jpg")

    dir_pic_name = []
    for url_p in corrected_urls:
        img_data = requests.get(url=url_p)
        file_img_name = (re.search(r'/(\d+)\.(\d+)\.jpg', url_p).group(1)
                         + '+' + re.search(r'/(\d+)\.(\d+)\.jpg', url_p).group(2))
        dir_pic_name.append(file_img_name + ".jpg")
        print(url_p)
        with open('photo_drmartens/' + file_img_name + ".jpg", 'wb') as handler:
            handler.write(img_data.content)
        time.sleep(random.uniform(1, 2))

    product_info = {
        "SKU": sku,
        "Product Name": product_name,
        "Product Link": link_to_the_product,
        "Category 1": category_1,
        "Category 2": category_2,
        "Category 3": category_3,
        "Color": color,
        "Product Information": details,
        "Image Names": ", ".join(dir_pic_name)
    }
    return product_info


def get_product_links(sheet, driver, workbook):
    with open('drmartens_urls_womens_shoes.txt', mode='r', encoding='utf-8') as file:
        for url_product in file:
            url_product = url_product.strip()

            driver.get(url_product)
            page_title = driver.title
            print(url_product)

            if "| Dr. Martens" in page_title:
                time.sleep(random.uniform(3, 5))
                product_info = scraper(driver, url_product)
                sheet.append(tuple(product_info.values()))
                workbook.save('Product Information.xlsx')

            elif page_title == "Help us verify real visitors, Dr. Martens":
                time.sleep(120)
                product_info = scraper(driver, url_product)
                sheet.append(tuple(product_info.values()))
                workbook.save('Product Information.xlsx')
            else:
                continue

        driver.close()


def create_workbook():
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    headers = [
        "SKU", 'Product Name', 'Product Link', 'Category 1',
        'Category 2', 'Category 3', 'Color', 'Product Information', 'Image Names'
    ]

    for col_num, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col_num).value = header

    return workbook, sheet


def main():
    with setup_driver() as driver:
        try:
            workbook, sheet = create_workbook()
            get_product_links(sheet, driver, workbook)
            file_name = "Product Information.xlsx"
            workbook.save(file_name)
            driver.quit()
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
