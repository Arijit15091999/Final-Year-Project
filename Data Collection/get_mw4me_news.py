from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import InvalidSessionIdException, TimeoutException
from colorama import Fore, Style, init
import pandas as pd
import os
import platform
import psutil
import time
from contextlib import contextmanager

# Initialize colorama
init()

# Global variables
FILE_PATH = "data.csv"
MAX_RETRIES = 3
PAGE_LOAD_TIMEOUT = 30
DELAY_BETWEEN_REQUESTS = 2  # seconds

year_page_map = {
    "2025": 1263,
    "2024": 4113,
    "2023": 3857,
    "2022": 3694,
    "2021": 2295,
    "2020": 1268,
    "2019": 1877,
    '2018': 1777,
    '2017': 1858,
    '2016': 2071,
    '2015': 1970,
    '2014': 1978,
    '2013': 1601,
    '2012': 1323,
    '2011': 394
}

@contextmanager
def selenium_driver(options):
    driver = webdriver.Firefox(options=options)
    try:
        yield driver
    finally:
        kill_driver(driver)

def process_date(date_string):
    try:
        arr = date_string.split('-')
        arr.reverse()
        return "-".join(arr)
    except Exception as e:
        print(f"{Fore.YELLOW}Date processing error: {e} for date {date_string}{Style.RESET_ALL}")
        return date_string  # Return original if processing fails

def store_data_into_csv(file_name, data):    
    try:
        dataframe = pd.DataFrame(
            data=data,
            columns=["Datetime", "News", "Link"]
        )
        
        dataframe.to_csv(
            path_or_buf=file_name,
            mode='a',
            index=False,
            encoding='utf-8',
            header=not os.path.isfile(file_name)
        )
    except Exception as e:
        print(f"{Fore.RED}Error saving to CSV: {e}{Style.RESET_ALL}")

def get_article_info():
    try:
        for page in range(961,year_page_map['2015']):
            result = get_article_by_year_and_page_number(2015, page + 1)
            if result:
                store_data_into_csv(FILE_PATH, result)
            time.sleep(DELAY_BETWEEN_REQUESTS)  # Delay between pages

        for year in range(2016, 2026):
            print(f"{Fore.BLUE}Processing year: {year}{Style.RESET_ALL}")
            get_article_by_year(str(year))
            time.sleep(DELAY_BETWEEN_REQUESTS)  # Be polite to the server
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}Process interrupted by user{Style.RESET_ALL}")
    finally:
        kill_all_instances_of_firefox_and_geckodriver()

def get_article_by_year(year):
    if year not in year_page_map:
        print(f"{Fore.RED}Year {year} not in page map{Style.RESET_ALL}")
        return
    
    number_of_pages = year_page_map[year]
    print(f"{Fore.CYAN}Found {number_of_pages} pages for year {year}{Style.RESET_ALL}")
    
    for page in range(number_of_pages):
        result = get_article_by_year_and_page_number(year, page + 1)
        if result:
            store_data_into_csv(FILE_PATH, result)
        time.sleep(DELAY_BETWEEN_REQUESTS)  # Delay between pages

def get_article_by_year_and_page_number(year, page):
    options = Options()
    options.add_argument("--headless")
    options.set_capability("pageLoadStrategy", "normal")
    
    all_results = []
    url = f"https://www.moneyworks4me.com/indianstocks/sectors-news-archives?year={year}&page={page}"
    
    for attempt in range(MAX_RETRIES):
        try:
            with selenium_driver(options) as driver:
                driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
                print(f"{Fore.GREEN}Fetching data (attempt {attempt + 1}) from {url}{Style.RESET_ALL}")
                
                driver.get(url=url)
                
                div_element = driver.find_element(
                    by=By.CSS_SELECTOR,
                    value="div#main-company-content"
                )
                
                li_elements = div_element.find_elements(by=By.TAG_NAME, value='li')
                
                for li in li_elements:
                    try:
                        anchor = li.find_element(by=By.TAG_NAME, value='a')
                        news_heading = anchor.text
                        news_link = anchor.get_attribute(name='href')
                        
                        date = li.find_element(
                            by=By.CSS_SELECTOR,
                            value="div>div"
                        ).text
                        
                        date = process_date(date)
                        
                        print(f"{Fore.CYAN}Found: {date} | {news_heading[:50]}...{Style.RESET_ALL}")
                        
                        all_results.append((date, news_heading, news_link))
                    except Exception as e:
                        print(f"{Fore.YELLOW}Error processing article: {e}{Style.RESET_ALL}")
                
                return all_results  # Return if successful
            
        except TimeoutException:
            if attempt < MAX_RETRIES - 1:
                print(f"{Fore.YELLOW}Timeout, retrying... ({attempt + 1}/{MAX_RETRIES}){Style.RESET_ALL}")
                time.sleep(5)
                continue
            print(f"{Fore.RED}Max retries reached for {url}{Style.RESET_ALL}")
            return []
        except Exception as e:
            print(f"{Fore.RED}Error: {type(e).__name__} - {str(e)}{Style.RESET_ALL}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(5)
                continue
            return []
    
    return []

def kill_driver(driver):
    if driver:
        try:
            driver.quit()
        except InvalidSessionIdException:
            print(f"{Fore.YELLOW}Driver already closed{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}Error closing driver: {e}{Style.RESET_ALL}")
            kill_process_tree(driver.service.process.pid)

def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass
    except Exception as e:
        print(f"{Fore.RED}Failed to kill process tree: {e}{Style.RESET_ALL}")

def kill_all_instances_of_firefox_and_geckodriver():
    try:
        if platform.system().lower() == "windows":
            os.system("taskkill /f /im firefox.exe >nul 2>&1")
            os.system("taskkill /f /im geckodriver.exe >nul 2>&1")
        else:
            os.system("pkill -f firefox >/dev/null 2>&1")
            os.system("pkill -f geckodriver >/dev/null 2>&1")
    except Exception as e:
        print(f"{Fore.YELLOW}Cleanup warning: {e}{Style.RESET_ALL}")

