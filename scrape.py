import argparse
import requests
import re 
import xml.etree.ElementTree as ET
import json

from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from urllib.parse import urljoin, urlparse

class colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def crawl_emails(base_url, max_links=50):
    visited_urls = set()
    queue = [base_url]
    base_domain = urlparse(base_url).netloc
    link_count = 0
    all_emails = set()

    while queue and link_count < max_links:
        url = queue.pop(0)
        if url in visited_urls:
            continue

        try:
            response = requests.get(url)
            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                visited_urls.add(url)

                links = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    absolute_url = urljoin(base_url, href)
                    if urlparse(absolute_url).netloc == base_domain:
                        links.append(absolute_url)

                queue.extend(links)
                link_count += 1

                page_text = soup.get_text()
                page_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', page_text)

                if page_emails:
                    for email in page_emails:
                        all_emails.add(email)

            else:
                None
                # print(colors.RED + f"Failed to retrieve {url}. Status code: {response.status_code}")

        except Exception as e:
            # write to log instead
            None
            # print(f"An error occurred while fetching {url}: {str(e)}")

    if all_emails:
        print(colors.GREEN + f"{all_emails}" + colors.RESET + " found on " + colors.YELLOW + f"{base_domain}")
        base_url_data = {"url": base_domain, "emails": list(all_emails)}
        with open("output.json", "a") as json_file:
            json.dump(base_url_data, json_file, indent=2)
            json_file.write(",\n")
    else:
        print(colors.RED + f"no emails found on {base_domain}")

def get_maps(keyword, location):
    return f"https://www.google.com/maps/search/{keyword}+in+{location}/"

def get_websites(driver, num_results):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    website_urls = []
    for link in soup.find_all('a', {'data-value': 'Website'}):
        website_url = link.get('href')
        if website_url and "https" in website_url:
            crawl_emails(website_url)
            sleep(5)
            website_urls.append(website_url)
            if len(website_urls) >= num_results:
                break
    return website_urls

def get_websites(driver, num_results):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    website_urls = []
    for link in soup.find_all('a', {'data-value': 'Website'}):
        website_url = link.get('href')
        if website_url and "https" in website_url:
            crawl_emails(website_url)
            sleep(5)
            website_urls.append(website_url)
            if len(website_urls) >= num_results:
                break
    return website_urls


def main(args):
    with open("output.json", "w") as json_file:
        json_file.write("[\n")

    options = webdriver.ChromeOptions()
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--enable-automation")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    keyword = args.keyword
    location = args.location
    url = get_maps(keyword, location)
    driver.get(url)
    sleep(4)
    print("Collecting map data from:", driver.current_url)

    website_urls = get_websites(driver, args.num_results)
    for url in website_urls:
        print(colors.YELLOW + "Website URL:", url)
    
    sleep(2)
    driver.quit()

    print(colors.GREEN + "Successfully saved all to output.json")
    with open("output.json", "a") as json_file:
        json_file.write("]\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Google Maps Web Scraper')
    parser.add_argument('-f', '--file', type=str, help='File containing keywords')
    parser.add_argument('-i', '--keyword', nargs='+', default="agency", type=str, help='Keywords to search for')
    parser.add_argument('-l', '--location', type=str, default='leeds', help='Location to search')
    parser.add_argument('-n', '--num_results', type=int, default=10, help='Number of businesses to scrape')
    args = parser.parse_args()
    main(args)
