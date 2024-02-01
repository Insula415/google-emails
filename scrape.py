import argparse
import requests
import re
import xml.etree.ElementTree as ET
import json
import time
import threading
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from urllib.parse import urljoin, urlparse
from datetime import datetime
from pynput.keyboard import Key, Listener

class colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    INVISIBLE = '\033[8m' 

all_ems = 0

def log(val):
    with open("log.txt", "a") as f:
        f.write(val)
        f.write("\n")

def on_press(key):
    None
    # if "q" or "Q" in format(key): 
    #     print("quit this and add some logic here...")

def keyboard_listener():
    with Listener(on_press=on_press) as listener:
        listener.join()

"""
Scrapes emails from webpages. Starts from the base URL and iterates through links found on each page. 

base_url = website url 
max_links = max number of links indexed from the base url
"""

def crawl_emails(base_url, max_links=50):
    global all_ems
    visited_urls = set()
    queue = [base_url]
    base_domain = urlparse(base_url).netloc
    link_count = 0
    all_emails = set()

    log(f"Going to {base_url}")

    while queue and link_count < max_links:
        url = queue.pop(0)
        if url in visited_urls:
            continue

        log(f"Scraping {url}")

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
                    log(f"Found email on {url}")

                for email in page_emails:
                    if '.com' in email or '.co.uk' in email:
                        index = email.rfind('.com') if '.com' in email else email.rfind('.co.uk')
                        stripped = email[:index + len('.com') if '.com' in email else index + len('.co.uk')]
                        all_emails.add(stripped)
                        all_ems += 1
                    else:
                        all_emails.add(email)
                        all_ems += 1

            else:
                with open("errors.txt", "a") as f:
                    f.write(f"Failed to retrieve {url}. Status code: {response.status_code}")
                    f.write("\n")

        except Exception as e:
            with open("errors.txt", "a") as f:
                f.write(f"An error occurred while fetching {url}: {str(e)}")
                f.write("\n")

    if all_emails:
        print(colors.GREEN + f"{all_emails}" + colors.RESET + " found on " + colors.YELLOW + f"{base_domain}" + colors.RESET)
        print(" ")
        base_url_data = {"url": base_domain, "emails": list(all_emails)}
        with open("output.json", "a") as json_file:
            json.dump(base_url_data, json_file, indent=2)
            json_file.write(",\n")
    else:
        print(colors.RED + f"no emails found on {base_domain}" + colors.RESET)
        print(" ")
    
def get_maps(keyword, location):
    return f"https://www.google.com/maps/search/{keyword}+in+{location}/"

def get_websites(driver, num_results):
    print("Scrolling for 10 seconds...")
    print(" ")
    scroll_box = driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')

    start_time = time.time()
    current_time = start_time

    while current_time - start_time < 10:  # Scroll for 10 seconds
        scroll_box = driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scroll_box)
        sleep(1) 
        current_time = time.time()
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    website_urls = []
    for link in soup.find_all('a', {'data-value': 'Website'}):
        website_url = link.get('href')
        if website_url and "https" in website_url:
            website_urls.append(website_url)
            if len(website_urls) >= num_results:
                break
    

    print(colors.BOLD + f"Websites found: {len(website_urls)}")

    webcount = 1
    for url in website_urls:
        print(f"Scraping {webcount} of {len(website_urls)}" + colors.RESET)
        crawl_emails(url)
        webcount += 1

    return website_urls

def main(args):
    print("*******************************************")
    print("*          "+colors.YELLOW+"Search Parameters"+colors.RESET+"              *")
    print("*******************************************")
    print("*"+colors.GREEN+ " File:"+colors.RESET+"       ", args.file if args.file else "Not specified")
    print("*" + colors.GREEN + " Headless?" + colors.RESET + "     ", args.headless)
    print("*"+colors.GREEN+" Keyword:    "+colors.RESET, args.keyword)
    print("*"+colors.GREEN+" Location:   "+colors.RESET, args.location)
    print("*"+colors.GREEN+" No. of Websites:"+colors.RESET, args.num_results)
    print("*******************************************")
    print(" ")
    print(colors.BOLD + "Logs are shown in logs.txt to clean up terminal. The code is NOT hanging. \n" )
    print("Alternatively errors are shown in errors.txt, these are basic url errors but provide good insight into what information is being scraped. \n" + colors.INVISIBLE)
    
    with open("output.json", "w") as json_file:
        json_file.write("[\n")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--enable-automation")
    if args.headless:
        options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    keyword = args.keyword
    location = args.location
    url = get_maps(keyword, location)
    start_time = datetime.now()
    driver.get(url)
    
    if "consent" in driver.current_url:
        print(colors.RESET + "Clicking reject...")
        driver.find_element(By.XPATH, "//span[text()='Reject all'] | //button[text()='Reject all'] | //div[text()='Reject all']").click()

    print("Searching:", driver.current_url)

    website_urls = get_websites(driver, args.num_results)
    
    driver.quit()
    print(" ")
    
    with open("output.json", "a") as json_file:
        json_file.write("]\n")

    end_time = datetime.now()
    total_time = end_time - start_time
    mins = total_time.total_seconds() // 60
    secs = total_time.total_seconds() % 60

    all_webs = len(website_urls)


    print(colors.GREEN + "Successfully saved all to output.json"+colors.BOLD)

    print(" ")
    print("*******************************************")
    print("*                 Statistics               *")
    print("*******************************************")
    print(colors.GREEN+"* Total number of websites: ", all_webs)
    print("* Total unique emails found: ", all_ems)
    print("* Total time taken to run: ", f"{mins:.0f} minutes {secs:.2f} seconds" + colors.RESET)

    with open("log.txt", "w") as f:
        f.write("Cleared log. Please run file again to get logs.")


if __name__ == "__main__":
    keyboard_thread = threading.Thread(target=keyboard_listener)
    keyboard_thread.start()

    parser = argparse.ArgumentParser(description='Google Maps Web Scraper')
    parser.add_argument('-f', '--file', type=str, help='File containing keywords')
    parser.add_argument('-i', '--keyword', nargs='+', default="agency", type=str,
                        help='Keywords to search for. Sentences should be concatenated with + e.g. website+agency')
    parser.add_argument('-l', '--location', type=str, default='leeds', help='Location to search')
    parser.add_argument('-n', '--num_results', type=int, default=10, help='Number of businesses to scrape')
    parser.add_argument('-headless', '--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('-help', action='help', help='Show this help message and exit')
    args = parser.parse_args()
    main(args)

    keyboard_thread.join()