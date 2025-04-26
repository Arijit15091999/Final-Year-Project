import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
import pandas as pd
import os
import time
from datetime import datetime

# Initialize colorama
init()

# Global variables
FILE_PATH = "data.csv"
MAX_RETRIES = 3
DELAY_BETWEEN_REQUESTS = 2  # seconds
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

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

def process_date(date_string):
    try:
        arr = date_string.split('-')
        arr.reverse()
        return "-".join(arr)
    except Exception as e:
        print(f"{Fore.YELLOW}Date processing error: {e} for date {date_string}{Style.RESET_ALL}")
        return date_string  # Return original if processing fails

# def process_date(date_string):
#     try:
#         # Parse the date string into a datetime object
#         date_obj = datetime.strptime(date_string, '%d-%m-%Y')
#         # Format it as YYYY-MM-DD
#         return date_obj.strftime('%Y-%m-%d')
#     except Exception as e:
#         print(f"{Fore.YELLOW}Date processing error: {e} for date {date_string}{Style.RESET_ALL}")
#         return date_string  # Return original if processing fails

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
        for page in range(1463, year_page_map['2016']):
            result = get_article_by_year_and_page_number(2016, page + 1)
            if result:
                store_data_into_csv(FILE_PATH, result)
            time.sleep(DELAY_BETWEEN_REQUESTS)

        for year in range(2017, 2026):
            print(f"{Fore.BLUE}Processing year: {year}{Style.RESET_ALL}")
            get_article_by_year(str(year))
            time.sleep(DELAY_BETWEEN_REQUESTS)
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}Process interrupted by user{Style.RESET_ALL}")

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
        time.sleep(DELAY_BETWEEN_REQUESTS)

def get_article_by_year_and_page_number(year, page):
    all_results = []
    url = f"https://www.moneyworks4me.com/indianstocks/sectors-news-archives?year={year}&page={page}"
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"{Fore.GREEN}Fetching data (attempt {attempt + 1}) from {url}{Style.RESET_ALL}")
            
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            soup = BeautifulSoup(response.text, 'html.parser')
            div_element = soup.find('div', id='main-company-content')
            
            if not div_element:
                print(f"{Fore.YELLOW}No content found on page {page}{Style.RESET_ALL}")
                return []
            
            li_elements = div_element.find_all('li')
            
            for li in li_elements:
                try:
                    anchor = li.find('a')
                    if not anchor:
                        continue
                        
                    news_heading = anchor.get_text(strip=True)
                    news_link = anchor.get('href', '')
                    
                    date_div = li.find('div')
                    if date_div:
                        date = date_div.get_text(strip=True)
                        date = process_date(date)
                    else:
                        date = "Unknown"
                    
                    print(f"{Fore.CYAN}Found: {date} | {news_heading[:50]}...{Style.RESET_ALL}")
                    all_results.append((date, news_heading, news_link))
                    
                except Exception as e:
                    print(f"{Fore.YELLOW}Error processing article: {e}{Style.RESET_ALL}")
            
            return all_results
            
        except requests.RequestException as e:
            print(f"{Fore.RED}Request failed: {e}{Style.RESET_ALL}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(5)
                continue
            return []
        except Exception as e:
            print(f"{Fore.RED}Error: {type(e).__name__} - {str(e)}{Style.RESET_ALL}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(5)
                continue
            return []
    
    return []

if __name__ == "__main__":
    get_article_info()