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
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    return webdriver.Chrome(options=options)


def scraper(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    all_product_container = soup.find('div', class_="product-list-container bfx-price-container")
    link_product = all_product_container.find_all('a')

    urls = []
    for item in link_product:
        base_section_url = item.get("href")
        urls.append(base_section_url)

    urls = list(set(urls))

    with open('../drmartens_urls_mens_shoes.txt', 'a') as file:
        for full_url in urls:
            if "page=" in full_url:
                continue
            else:
                file.write(f"https://www.drmartens.com{full_url}\n")


def get_product_links(driver):
    urls = ['https://www.drmartens.com/us/en/mens/c/02000000?dmstyle=airwair&dmstyle=boots&dmstyle=sandals&dmstyle'
            '=shoes&page=0',
            'https://www.drmartens.com/us/en/mens/c/02000000?dmstyle=airwair&dmstyle=boots&dmstyle=sandals&dmstyle'
            '=shoes&page=1',
            'https://www.drmartens.com/us/en/mens/c/02000000?dmstyle=airwair&dmstyle=boots&dmstyle=sandals&dmstyle'
            '=shoes&page=2',
            'https://www.drmartens.com/us/en/mens/c/02000000?dmstyle=airwair&dmstyle=boots&dmstyle=sandals&dmstyle'
            '=shoes&page=3',
            'https://www.drmartens.com/us/en/mens/c/02000000?dmstyle=airwair&dmstyle=boots&dmstyle=sandals&dmstyle'
            '=shoes&page=4',
            'https://www.drmartens.com/us/en/mens/c/02000000?dmstyle=airwair&dmstyle=boots&dmstyle=sandals&dmstyle'
            '=shoes&page=5',
            'https://www.drmartens.com/us/en/mens/c/02000000?dmstyle=airwair&dmstyle=boots&dmstyle=sandals&dmstyle'
            '=shoes&page=6',
            'https://www.drmartens.com/us/en/mens/c/02000000?dmstyle=airwair&dmstyle=boots&dmstyle=sandals&dmstyle'
            '=shoes&page=7',
            ]

    for url in urls:
        driver.get(url)
        page_title = driver.title
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        page_param = "page=" + str(query_params["page"][0])
        print(f'Итерация: {page_param}')

        if page_title == "Men's Footwear | Boots, Shoes & Sandals | Dr. Martens":
            time.sleep(random.uniform(3, 5))
            scraper(driver)

        elif page_title == "Help us verify real visitors, Dr. Martens":
            time.sleep(120)
            scraper(driver)
        else:
            continue

    driver.close()


def main():
    driver = setup_driver()
    get_product_links(driver)
    driver.quit()


if __name__ == "__main__":
    main()
