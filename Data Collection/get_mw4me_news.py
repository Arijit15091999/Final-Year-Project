from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import InvalidSessionIdException
from colorama import Fore, Style, init
import pandas as pd
import numpy as np
import os
import platform
import subprocess
import psutil

# Global variables
FILE_PATH = "data.csv"

year_page_map = {
    "2025" : 1263,
    "2024" : 4113,
    "2023" : 3857,
    "2022" : 3694,
    "2021" : 2295,
    "2020" : 1268,
    "2019" : 1877,
    '2018' : 1777,
    '2017' : 1858,
    '2016' : 2071,
    '2015' : 1970,
    '2014' : 1978,
    '2013' : 1601,
    '2012' : 1323,
    '2011' : 394
}

def process_date(date_string):
    arr = date_string.split('-')
    arr.reverse()
    
    return "-".join(arr)

def store_data_into_csv(file_name, data):    
    dataframe = pd.DataFrame(
        data = data,
        columns = [
            "Datetime",
            "News",
            "Link"
        ]
    )
    
    dataframe.to_csv(
        path_or_buf = file_name,
        mode = 'a',
        index=False,
        encoding='utf-8',
        header = not os.path.isfile(file_name)
    )
    

def get_article_info():
    for year in range(2011, 2026):
        get_article_by_year(str(year))

def get_article_by_year(year):
    number_of_pages = year_page_map[year]
    
    # print(number_of_pages)
    all_results = []
    
    for page in range(number_of_pages):
        result = get_article_by_year_and_page_number(year, page + 1)
        store_data_into_csv(
            file_name = FILE_PATH,
            data = result
        )    
    
def get_article_by_year_and_page_number(year,page):
    try:
        # Configure Firefox options
        options = Options()
        options.add_argument("--headless")
        
        # Set page load timeout
        options.set_capability("pageLoadStrategy", "normal")

        # init driver
        driver = webdriver.Firefox(options = options)
        driver.set_page_load_timeout(30)
        
        url = f"https://www.moneyworks4me.com/indianstocks/sectors-news-archives?year={year}&page={page}"

        print(f"{Fore.GREEN}Fetching data from {url} {Style.RESET_ALL}")
        
        driver.get(
            url = url
        )

        # print(driver.title)
        
        div_element = driver.find_element(
            by = By.CSS_SELECTOR,
            value = "div#main-company-content"
        )
        
        li_element_for_news = div_element.find_elements(
            by = By.TAG_NAME, 
            value = 'li'
        )
        
        all_results = []
        
        for li in li_element_for_news:
            anchor = li.find_element(
                by = By.TAG_NAME,
                value = 'a'
            )
            news_heading = anchor.text
            news_link = anchor.get_attribute(
                name = 'href'
            )
            
            date = li.find_element(
                by = By.CSS_SELECTOR,
                value = "div>div"
            ).text
            
            # print(date)
            # print(news_heading)
            # print(news_link)
            
            date = process_date(date)
            
            print(f"{Fore.CYAN}Data Found date = {date}, heading = {news_heading} {url} {Style.RESET_ALL}")
            
            all_results.append(
                (date, news_heading, news_link)
            )
    except KeyboardInterrupt:
        kill_driver(driver = driver)
    except Exception as e:
        print(f"{Fore.RED}Exception occured {e} {Style.RESET_ALL}")
    finally:
        kill_driver(driver=driver)
        
    return all_results
    
def kill_driver(driver):
    if driver:
        try:
            driver.quit()
        except InvalidSessionIdException:
            print(f"{Fore.YELLOW} Driver already closed {Style.RESET_ALL}")
        except Exception as e:
            kill_process_tree(driver.service.process.pid)
            
            

def kill_process_tree(pid):
    parent = psutil.Process(pid)

    try:
        for child in parent.children:
            child.kill()
        parent.kill()
    except Exception as e:
        print(f"{Fore.RED} failed to kill the process_tree{Style.RESET_ALL}")


def kill_all_instances_of_firefox_and_geckodriver():
    current_os = platform.system().lower()

    try:
        if current_os == "windows":
            subprocess.run("cmd", "/c", "taskkill /F /IM firefox.exe")
            subprocess.run("cmd", "/c", "taskkill /F /IM geckodriver.exe")
            print(f"{Fore.GREEN} Ran Windows commands. {Style.RESET_ALL}")

        elif current_os == "linux" or current_os == "darwin":
            subprocess.run("pkill -f firefox", shell=True, check=True)
            subprocess.run("pkill -f geckodriver", shell=True, check=True)
            print(f"{Fore.GREEN} Ran Unix commands. {Style.RESET_ALL}")
        else:
            print(f"{Fore.RED} OS not supported {Style.RESET_ALL}")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Command failed: {e}{Style.RESET_ALL}")

# if __name__ == "__main__":
#     print(process_date("23-04-2025"))
#     get_article_by_year(str(2025))