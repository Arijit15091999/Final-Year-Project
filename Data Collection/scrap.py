import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import os
import calendar
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

BASE_URL = "https://economictimes.indiatimes.com/archivelist"

month = 1


# sep, apr, june, nov = 30
dateMonthMap = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def getDataForYear(year, startMonthIndex, endMonthIndex, index):
    filename = "data.csv"

    try:
        driver = webdriver.Firefox()

        if(year % 4 == 0):
                dateMonthMap[2] = 29
        else:
            dateMonthMap[2] = 28

        for month in range(startMonthIndex, endMonthIndex + 1):

            for day in range(1, dateMonthMap[month] + 1):
                url = f"{BASE_URL}/year-{year},month-{str(month)}," + f"starttime-{str(index)}.cms"
                print(f"{Fore.CYAN}Fetching data from: {url}{Style.RESET_ALL}")


                data = []

                # print(url)

                try:
                    driver.get(url = url)

                    news = driver.find_element(by = By.CSS_SELECTOR, value = "ul.content")

                    listOfNews = news.find_elements(by = By.TAG_NAME, value = "li")
                    # print(len(listOfNews))

                    for news in listOfNews:
                        headLine = news.text
                        newsLink = news.find_element(by = By.TAG_NAME, value = 'a').get_attribute(name = "href")
                        newsDate = datetime(year = year, month = month, day = day).strftime("%Y-%m-%d")
                        print(headLine)
                        # print(newsLink)
                        print(newsDate)


                        data.append([newsDate, headLine, newsLink])

                except Exception as e:
                    print(f"{Fore.RED}Error fetching data for {year}-{month}-{day}: {e}{Style.RESET_ALL}")

                if data:
                    # filename = f"economic_times_news_{year}_{month:02d}_{day:02d}.csv"
                    df = pd.DataFrame(data, columns=["Datetime", "News", "Link"])
                    df.to_csv(filename, mode='a', index=False, header=not os.path.exists(filename), encoding="utf-8")
                    print(f"{Fore.GREEN}✅ Data saved for {year}-{month:02d}-{day:02d} in {filename}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️ No news found for {year}-{month:02d}-{day:02d}{Style.RESET_ALL}")

                index += 1

        print("updatedIndex = ", index)
    finally:
        driver.quit()


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
