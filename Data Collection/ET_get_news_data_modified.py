from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import (NoSuchElementException, TimeoutException,
                                        StaleElementReferenceException, WebDriverException,
                                        InvalidSessionIdException)
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from colorama import Fore, Style, init
import pandas as pd
import os
import time
from urllib3.exceptions import ReadTimeoutError
from selenium.webdriver.firefox.service import Service
import warnings
import psutil
import platform
import subprocess

init(autoreset=True)

# Global Constants
INPUT_FILE = "data.csv"
OUTPUT_FILE = "ET_data.csv"
NUM_PROCESSES = min(4, os.cpu_count() - 1)


def init_driver():
    """Initialize and return a new Selenium WebDriver instance."""
    options = Options()
    options.add_argument("--headless")
    options.set_preference("intl.accept_languages", "en,en-US")
    options.binary_location = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"

    service = Service(executable_path="./geckodriver.exe")

    driver = webdriver.Firefox(options=options, service=service)
    driver.set_page_load_timeout(180)

    warnings.simplefilter("ignore")
    return driver


def kill_process_tree(pid):
    parent = psutil.Process(pid)

    try:
        for child in parent.children:
            child.kill()
        parent.kill()
    except Exception as e:
        print(f"{Fore.RED} failed to kill the process_tree{Style.RESET_ALL}")


def fetch_article_text(link):
    """Fetch article text from a given link using Selenium."""
    driver = None
    text = None
    try:
        driver = init_driver()
        for attempt in range(3):  # Retry up to 3 times
            try:
                print(f"{Fore.GREEN}✔️ Fetching: {link} (Attempt {attempt + 1}){Style.RESET_ALL}")
                driver.get(link)

                # Remove ads and pop-ups
                script = """
                    let srWidget = document.getElementById("sr_widget");
                    if (srWidget) srWidget.remove();
                    Array.from(document.getElementsByClassName('growfast_widget')).forEach(e => e.remove());
                """
                driver.execute_script(script)

                # Extract article content
                article_element = driver.find_element(By.CLASS_NAME, "artText")
                article_text = article_element.text.strip()

                if article_text:
                    text = article_text  # Successful fetch

            except (NoSuchElementException, TimeoutException):
                print(f"{Fore.RED}❌ Error: Article not found on {link}, retrying...{Style.RESET_ALL}")
                time.sleep(2)
            except ReadTimeoutError:
                print(f"{Fore.RED}Read Timeout on {link}, skipping...{Style.RESET_ALL}")
            except StaleElementReferenceException:
                print(f"{Fore.YELLOW} Stale Element error: Retrying... {Style.RESET_ALL}")
            except WebDriverException as e:
                print(f"{Fore.RED} WebDriver error: {e} {Style.RESET_ALL}")
    except KeyboardInterrupt:
        kill_all_instances_of_firefox_and_geckodriver()
    except Exception as e:
        print(f"{Fore.RED} Unexpected error: {e} {Style.RESET_ALL}")

    finally:
        if driver:
            try:
                driver.quit()
            except InvalidSessionIdException:
                print(f"{Fore.YELLOW} Driver already closed {Style.RESET_ALL}")
            except Exception as e:
                kill_process_tree(driver.service.process.pid)

    return link, text


def process_links_in_parallel(links):
    """Process multiple links in parallel using threads."""
    print(f"{Fore.CYAN}🔹 Using {NUM_PROCESSES} parallel threads...{Style.RESET_ALL}")

    with Pool(NUM_PROCESSES) as executor:
        results = list(executor.map(fetch_article_text, links))

    return results


def scrape_news():
    """Main function to scrape news articles from links in data.csv."""
    if not os.path.exists(INPUT_FILE):
        print(f"{Fore.RED}❌ Error: '{INPUT_FILE}' not found!{Style.RESET_ALL}")
        return

    df = pd.read_csv(INPUT_FILE)

    if "Link" not in df.columns:
        print(f"{Fore.RED}❌ Error: 'Link' column missing in CSV!{Style.RESET_ALL}")
        return

    links = df["Link"].dropna().tolist()

    # when the scrapping stops unexpectedly
    already_scrapped_links = set()
    if os.path.exists(OUTPUT_FILE):
        already_scrapped_links = set(
            pd.read_csv(OUTPUT_FILE)["Link"].dropna().tolist()
        )

    # filter the links if they are already processed

    links = [link for link in links if link not in already_scrapped_links]

    # Split into batches to avoid excessive memory usage
    batch_size = 500
    total_batches = (len(links) // batch_size) + 1

    all_results = []

    for i in range(total_batches):
        batch_links = links[i * batch_size: (i + 1) * batch_size]
        print(f"{Fore.YELLOW}📌 Processing batch {i + 1}/{total_batches} ({len(batch_links)} links){Style.RESET_ALL}")

        results = process_links_in_parallel(batch_links)  # Removed `[0]`
        all_results.extend(results)

        # Save intermediate results 
        temp_df = pd.DataFrame(all_results, columns=["Link", "Text"])
        temp_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"{Fore.GREEN}✔️ Scraping complete! Data saved to '{OUTPUT_FILE}'{Style.RESET_ALL}")

    kill_all_instances_of_firefox_and_geckodriver()


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

# Run the scraper
# if __name__ == "__main__":
#    scrape_news()
