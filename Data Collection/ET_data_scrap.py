import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime
import os
import calendar
from colorama import Fore, Style, init
from selenium.webdriver.firefox.options import Options
import time


# # Initialize colorama
# init(autoreset=True)

# BASE_URL = "https://economictimes.indiatimes.com/archivelist"

# month = 1

# # sep, apr, june, nov = 30
# dateMonthMap = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


# def getDataForYear(year, startMonthIndex, endMonthIndex, index):
#     filename = "data.csv"

#     # options for headlesss so that we dont need to install firefox
#     options = Options()
#     options.add_argument("--headless")

#     try:
#         driver = webdriver.Firefox(
#             options = options
#         )

#         if(year % 4 == 0):
#                 dateMonthMap[2] = 29
#         else:
#             dateMonthMap[2] = 28

#         for month in range(startMonthIndex, endMonthIndex + 1):

#             for day in range(1, dateMonthMap[month] + 1):
#                 url = f"{BASE_URL}/year-{year},month-{str(month)}," + f"starttime-{str(index)}.cms"
#                 print(f"{Fore.CYAN}Fetching data from: {url}{Style.RESET_ALL}")


#                 data = []

#                 # print(url)

#                 try:
#                     driver.get(url = url)

#                     news = driver.find_element(by = By.CSS_SELECTOR, value = "ul.content")

#                     listOfNews = news.find_elements(by = By.TAG_NAME, value = "li")
#                     # print(len(listOfNews))

#                     for news in listOfNews:
#                         headLine = news.text
#                         newsLink = news.find_element(by = By.TAG_NAME, value = 'a').get_attribute(name = "href")
#                         newsDate = datetime(year = year, month = month, day = day).strftime("%Y-%m-%d")
#                         print(headLine)
#                         # print(newsLink)
#                         print(newsDate)


#                         data.append([newsDate, headLine, newsLink])

#                 except Exception as e:
#                     print(f"{Fore.RED}Error fetching data for {year}-{month}-{day}: {e}{Style.RESET_ALL}")

#                 if data:
#                     # filename = f"economic_times_news_{year}_{month:02d}_{day:02d}.csv"
#                     df = pd.DataFrame(data, columns=["Datetime", "News", "Link"])
#                     df.to_csv(filename, mode='a', index=False, header=not os.path.exists(filename), encoding="utf-8")
#                     print(f"{Fore.GREEN}✅ Data saved for {year}-{month:02d}-{day:02d} in {filename}{Style.RESET_ALL}")
#                 else:
#                     print(f"{Fore.YELLOW}⚠️ No news found for {year}-{month:02d}-{day:02d}{Style.RESET_ALL}")

#                 index += 1

#         print("updatedIndex = ", index)
#     finally:
#         driver.quit()


# def storeDataToCsv(data):
#     dataFrame = pd.DataFrame(data = data, columns=["datetime", "article-heading", "article-link"])
#     filename = "data.csv"
#     dataFrame.to_csv(
#         filename,
#         mode='a',
#         index=False,
#         header=not pd.io.common.file_exists(filename),
#         encoding="utf-8"
#     )


# Initialize colorama
init(autoreset=True)

BASE_URL = "https://economictimes.indiatimes.com/archivelist"
WAIT_TIMEOUT = 10  # seconds to wait for elements to load
RETRY_ATTEMPTS = 3  # number of retries if page fails to load

month = 1
dateMonthMap = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def getDataForYear(year, startMonthIndex, endMonthIndex, index):
    filename = "data.csv"

    # Configure Firefox options
    options = Options()
    options.add_argument("--headless")
    
    # Set page load timeout
    options.set_capability("pageLoadStrategy", "normal")

    try:
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(30)  # 30 seconds timeout for page load

        if year % 4 == 0:
            dateMonthMap[2] = 29
        else:
            dateMonthMap[2] = 28

        for month in range(startMonthIndex, endMonthIndex + 1):
            for day in range(1, dateMonthMap[month] + 1):
                url = f"{BASE_URL}/year-{year},month-{str(month)},starttime-{str(index)}.cms"
                print(f"{Fore.CYAN}Fetching data from: {url}{Style.RESET_ALL}")

                data = []
                success = False
                
                for attempt in range(RETRY_ATTEMPTS):
                    try:
                        driver.get(url=url)
                        
                        # Wait for either the content or the "no articles" message to appear
                        try:
                            # First check if there's a "no articles" message
                            no_articles = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'No Article(s) Found') or contains(text(), 'no articles')]"))
                            )
                            print(f"{Fore.YELLOW}⚠️ No articles found for {year}-{month:02d}-{day:02d}{Style.RESET_ALL}")
                            success = True
                            break
                            
                        except TimeoutException:
                            # If no "no articles" message, look for the content
                            news = WebDriverWait(driver, WAIT_TIMEOUT).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.content"))
                            )
                            
                            listOfNews = news.find_elements(By.TAG_NAME, "li")
                            
                            for news_item in listOfNews:
                                try:
                                    headLine = news_item.text
                                    newsLink = news_item.find_element(By.TAG_NAME, 'a').get_attribute("href")
                                    newsDate = datetime(year=year, month=month, day=day).strftime("%Y-%m-%d")
                                    print(f"{Fore.GREEN}Headline: {headLine}{Style.RESET_ALL}")
                                    print(f"Link: {newsLink}")
                                    print(f"Date: {newsDate}")
                                    
                                    data.append([newsDate, headLine, newsLink])
                                    
                                except NoSuchElementException:
                                    print(f"{Fore.YELLOW}⚠️ Incomplete news item found, skipping{Style.RESET_ALL}")
                                    continue
                            
                            success = True
                            break
                            
                    except Exception as e:
                        print(f"{Fore.RED}Attempt {attempt + 1} failed for {year}-{month:02d}-{day:02d}: {str(e)}{Style.RESET_ALL}")
                        if attempt < RETRY_ATTEMPTS - 1:
                            time.sleep(2)  # wait before retrying
                            continue
                        else:
                            print(f"{Fore.RED}❌ Failed to fetch data for {year}-{month:02d}-{day:02d} after {RETRY_ATTEMPTS} attempts{Style.RESET_ALL}")
                            break
                
                if success and data:
                    df = pd.DataFrame(data, columns=["Datetime", "News", "Link"])
                    df.to_csv(filename, mode='a', index=False, header=not os.path.exists(filename), encoding="utf-8")
                    print(f"{Fore.GREEN}✅ Data saved for {year}-{month:02d}-{day:02d} in {filename}{Style.RESET_ALL}")
                elif not data:
                    print(f"{Fore.YELLOW}⚠️ No news data collected for {year}-{month:02d}-{day:02d}{Style.RESET_ALL}")
                
                index += 1

        print(f"Final updatedIndex = {index}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Fatal error: {str(e)}{Style.RESET_ALL}")
    finally:
        try:
            driver.quit()
        except:
            pass

# Example usage:
# getDataForYear(2008, 1, 12, 1)
