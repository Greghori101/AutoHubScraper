from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
import time
import undetected_chromedriver as uc

# Path to the ChromeDriver executable
chrome_path = "/usr/local/bin/chromedriver"  # Update this to your actual path

# Chrome options to set headers and user-agent
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
)

service = Service(chrome_path)
dr = uc.Chrome(options=chrome_options)


# Define the base URL and start URL
base_url = "https://partsouq.com"
start_url = "https://partsouq.com"


# Function to get data from the URL
def fetch_url(url):
    dr.get(url)  # Random delay to avoid detection
    return dr.page_source


# Parse HTML using BeautifulSoup
from bs4 import BeautifulSoup


def parse_html(html):
    return BeautifulSoup(html, "html.parser")


# Function to get brands
def get_brands(soup):
    brand_links = [a["href"] for a in soup.select(".item a")]
    return [base_url + link for link in brand_links]


# Functions to get models, car names, groups, and parts...
# (similar to previous examples but adapted to work with Selenium)


def get_models(brand_url):
    html = fetch_url(brand_url)
    soup = parse_html(html)
    model_links = [a["href"] for a in soup.select("a.accordion-toggle, .in td a")]
    return [base_url + link for link in model_links]


def get_car_names(model_url):
    html = fetch_url(model_url)
    soup = parse_html(html)
    carname_links = [a["href"] for a in soup.select('[data-title="Name"] a')]
    return [base_url + link for link in carname_links]


def get_groups_link(carname_url):
    html = fetch_url(carname_url)
    soup = parse_html(html)
    groups_link = soup.select_one(".nav-tabs li:nth-of-type(3) a")
    if groups_link:
        return base_url + groups_link["href"]
    return None


def get_group_details(groups_link_url):
    html = fetch_url(groups_link_url)
    soup = parse_html(html)
    groupnames = [
        td.get_text(strip=True)
        for td in soup.select("tr.treegrid-collapsed:nth-of-type(n+2) td")
    ]
    group_links = [a["href"] for a in soup.select("td a")]
    group_links = [base_url + link for link in group_links]
    return groupnames, group_links


def get_parts(group_link_url):
    html = fetch_url(group_link_url)
    soup = parse_html(html)
    part_rows = soup.select("tr.part-search-tr")
    parts = []
    for row in part_rows:
        part_number = row.select_one("a").get_text(strip=True)
        part_name = row.select_one("td:nth-of-type(2)").get_text(strip=True)
        part_image_code = row.select_one("td.codeonimage").get_text(strip=True)
        part_amount_image = row.select_one("td:nth-of-type(4)").get_text(strip=True)
        parts.append(
            {
                "part_number": part_number,
                "part_name": part_name,
                "part_image_code": part_image_code,
                "part_amount_image": part_amount_image,
            }
        )
    return parts


# Open a CSV file to write the data
with open("parts_data.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(
        [
            "Brand",
            "Model",
            "Car Name",
            "Group Name",
            "Part Number",
            "Part Name",
            "Part Image Code",
            "Part Amount Image",
        ]
    )

    html = fetch_url(start_url)
    soup = parse_html(html)
    brands = get_brands(soup)

    for brand in brands:
        models = get_models(brand)
        for model in models:
            carnames = get_car_names(model)
            for carname in carnames:
                groups_link = get_groups_link(carname)
                if groups_link:
                    groupnames, group_links = get_group_details(groups_link)
                    for groupname, group_link in zip(groupnames, group_links):
                        parts = get_parts(group_link)
                        for part in parts:
                            writer.writerow(
                                [
                                    brand,
                                    model,
                                    carname,
                                    groupname,
                                    part["part_number"],
                                    part["part_name"],
                                    part["part_image_code"],
                                    part["part_amount_image"],
                                ]
                            )
                        time.sleep(1)  # Introduce random delay to avoid detection
                time.sleep(1)
            time.sleep(1)
        time.sleep(1)

# Close the browser
dr.quit()
