from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from colorama import Fore, Style, init
import pandas as pd
import os
import time

init(autoreset=True)

link = "https://economictimes.indiatimes.com/markets/stocks/news/stock-picks-of-the-week-4-stocks-with-consistent-score-improvement-and-upside-potential-of-up-to-27/articleshow/106442323.cms"

def getNewsTextFromLinkHelper(link, retryCount = 3):
    options = Options()
    options.add_argument("--headless")  # Enable headless mode

    data = "Not Found"

    try:
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(180)
        print(f"{Fore.CYAN}Fetching data from: {link}{Style.RESET_ALL}")
        driver.get(link)

        print(f"{Fore.GREEN}✔️ Successfully loaded page{Style.RESET_ALL}")

        # JavaScript to remove unwanted elements
        script = """
            let srWidget = document.getElementById("sr_widget");
            if (srWidget) srWidget.remove();
            Array.from(document.getElementsByClassName('growfast_widget')).forEach(e => e.remove());
        """
        driver.execute_script(script)

        try:
            articleText = driver.find_element(By.CLASS_NAME, "artText")
            data = articleText.text.strip()
            
            print(data)

            return data
        
        except NoSuchElementException:
            print(f"{Fore.RED}❌ Article content not found!{Style.RESET_ALL}")

    finally:
        driver.quit()

    if data == "Not Found":
        print(f"{Fore.YELLOW}⚠️ No news found {Style.RESET_ALL}")
        

    return data

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import time

# options = Options()
# # options.add_argument("--headless")  # Try running without headless mode
# options.set_preference("intl.accept_languages", "en,en-US")

# def getNewsTextFromLinkHelper(link, retries=3):
#     options = Options()
#     options.add_argument("--headless")  # Try running without headless mode
#     options.set_preference("intl.accept_languages", "en,en-US")
#     for attempt in range(retries):
#         try:
#             driver = webdriver.Firefox(options=options)
#             driver.set_page_load_timeout(180)  # Increased timeout
#             driver.get(link)
#             print(f"✔️ Successfully loaded page on attempt {attempt + 1}")

#             # JavaScript to remove ads
#             script = """
#                 let srWidget = document.getElementById("sr_widget");
#                 if (srWidget) srWidget.remove();
#                 Array.from(document.getElementsByClassName('growfast_widget')).forEach(e => e.remove());
#             """
#             driver.execute_script(script)

#             # Extract article text
#             articleText = driver.find_element(By.CLASS_NAME, "artText").text
#             driver.quit()
#             return articleText

#         except TimeoutException:
#             print(f"⏳ Attempt {attempt + 1}: Timeout error, retrying...")
#             time.sleep(5)
#         except NoSuchElementException:
#             print("❌ Article not found.")
#             break

#     return "Not Found"



# getNewsTextFromLinkHelper(link)


def getNewsFromLink():
    filename = "ET_data.csv"

    # Check if data.csv exists
    if not os.path.exists("data.csv"):
        print(f"{Fore.RED}❌ Error: 'data.csv' not found!{Style.RESET_ALL}")
        return

    dataFrame = pd.read_csv("data.csv")

    if "Link" not in dataFrame.columns:
        print(f"{Fore.RED}❌ Error: 'Link' column not found in CSV!{Style.RESET_ALL}")
        return

    links = dataFrame["Link"]
    texts = []

    # print(len(links))

    # for link in links:
    #     texts.append(getNewsTextFromLinkHelper(link))

    # list = ["https://economictimes.indiatimes.com/news/international/world-news/us-appeals-court-judges-skeptical-of-donald-trump-immunity-claim/articleshow/106676470.cms",
    #         "https://economictimes.indiatimes.com/news/international/us/los-angeles-lakers-vs-los-angeles-clippers-start-time-how-to-watch-nba-game-for-free/articleshow/106617995.cms",
    #         "https://economictimes.indiatimes.com/industry/services/property-/-cstruction/credai-to-certify-1-lakh-homes-25-million-sq-ft-of-commercial-real-estate-with-green-building-certifications/articleshow/106629427.cms",
    #         "https://economictimes.indiatimes.com/wealth/plan/financial-divide-in-a-family-how-parents-and-adult-children-can-recognise-and-resolve-it/articleshow/106589874.cms"
    #         ]
    for index, link in enumerate(links):
        print(f"{Fore.GREEN}count = {index + 1}{Style.RESET_ALL}")
        texts.append(getNewsTextFromLinkHelper(link))

    # print(len(texts))

    # dataFrame["Text"] = texts

    # # Save to CSV (avoid duplicates)
    # dataFrame.to_csv(filename, mode='w', index=False, encoding="utf-8")
    # print(f"{Fore.GREEN}✔️ Data saved to {filename}{Style.RESET_ALL}")


# getNewsFromLink()
