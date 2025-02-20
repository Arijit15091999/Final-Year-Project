from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from multiprocessing import Pool, cpu_count
from colorama import Fore, Style, init
import pandas as pd
import os
import time
from urllib3.exceptions import ReadTimeoutError

init(autoreset=True)

# Global Constants
INPUT_FILE = "data.csv"
OUTPUT_FILE = "ET_data.csv"
NUM_PROCESSES = max(2, cpu_count() - 1)  


def init_driver():
    """Initialize and return a new Selenium WebDriver instance."""
    options = Options()
    options.add_argument("--headless") 
    options.set_preference("intl.accept_languages", "en,en-US")

    driver = webdriver.Firefox(options=options)
    driver.set_page_load_timeout(180)
    return driver


def fetch_article_text(link):
    """Fetch article text from a given link using Selenium."""
    driver = init_driver()
    
    for attempt in range(3):  # Retry up to 3 times
        try:
            print(f"{Fore.GREEN}✔️ Fetching: {link} (Attempt {attempt + 1}){Style.RESET_ALL}")
            driver.get(link)

            # Remove ads and pop-ups using JavaScript
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
                driver.quit()
                return link, article_text

        except (NoSuchElementException, TimeoutException):
            print(f"{Fore.RED}❌ Error: Article not found on {link}, retrying...{Style.RESET_ALL}")
            time.sleep(2)  # Wait before retrying
        except ReadTimeoutError:
            print(f"{Fore.RED}Read Timeout on {link}, skipping...{Style.RESET_ALL}")
            time.sleep(3)

    driver.quit()

    return link, "Not Found"


def process_links_in_parallel(links):
    """Process multiple links in parallel using multiprocessing."""
    print(f"{Fore.CYAN}🔹 Using {NUM_PROCESSES} parallel processes...{Style.RESET_ALL}")

    with Pool(NUM_PROCESSES) as pool:
        results = pool.map(fetch_article_text, links)  # Parallel execution

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

    links = df["Link"].tolist()

    # Split into batches to avoid excessive memory usage
    batch_size = 500  # Adjust based on system performance
    total_batches = (len(links) // batch_size) + 1

    all_results = []

    for i in range(total_batches):
        batch_links = links[i * batch_size : (i + 1) * batch_size]
        print(f"{Fore.YELLOW}📌 Processing batch {i + 1}/{total_batches} ({len(batch_links)} links){Style.RESET_ALL}")

        results = process_links_in_parallel(batch_links)
        all_results.extend(results)

        # Save intermediate results to avoid data loss
        temp_df = pd.DataFrame(all_results, columns=["Link", "Text"])
        temp_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"{Fore.GREEN}✔️ Scraping complete! Data saved to '{OUTPUT_FILE}'{Style.RESET_ALL}")


# # Run the scraper
# if __name__ == "__main__":
#     scrape_news()
