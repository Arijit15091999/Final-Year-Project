import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from urllib3.exceptions import ReadTimeoutError
from multiprocessing import Pool
from colorama import Fore, Style, init
import pandas as pd
import os
import time
from urllib3.exceptions import ReadTimeoutError

init(autoreset=True)

# Global Constants
INPUT_FILE = "data.csv"
OUTPUT_FILE = "ET_data.csv"
NUM_PROCESSES = min(6, os.cpu_count() - 1)

def fetch_article_text(link):
    """Fetch article text from a given link using BeautifulSoup."""
    text = "Not Found"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(3):  # Retry up to 3 times
        try:
            print(f"{Fore.GREEN}Fetching: {link} (Attempt {attempt + 1}){Style.RESET_ALL}")
            
            # Get page content with timeout
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()  # Raise exception for bad status codes
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find article content - adjust selector as needed
            article_element = soup.find(class_="artText")
            
            if article_element:
                article_text = article_element.get_text().strip()
                if article_text:
                    text = article_text
                    return link, text
            
            print(f"{Fore.RED}Error: Article not found on {link}, retrying...{Style.RESET_ALL}")
            time.sleep(2)
            
        except ReadTimeoutError:
            print(f"{Fore.YELLOW}Read Timeout on {link}, skipping...{Style.RESET_ALL}")
            return link, "Not Found"
        except RequestException as e:
            print(f"{Fore.RED}Request error: {e}{Style.RESET_ALL}")
            time.sleep(2)
        except Exception as e:
            print(f"{Fore.RED} error: {e}{Style.RESET_ALL}")
            time.sleep(2)
    
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
        print(f"{Fore.RED}Error: '{INPUT_FILE}' not found!{Style.RESET_ALL}")
        return

    df = pd.read_csv(INPUT_FILE)

    if "Link" not in df.columns:
        print(f"{Fore.RED}Error: 'Link' column missing in CSV!{Style.RESET_ALL}")
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
        print(f"{Fore.YELLOW}Processing batch {i + 1}/{total_batches} ({len(batch_links)} links){Style.RESET_ALL}")

        results = process_links_in_parallel(batch_links)  # Removed `[0]`
        all_results.extend(results)

        # Save intermediate results 
        temp_df = pd.DataFrame(all_results, columns=["Link", "Text"])
        temp_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"{Fore.GREEN}✔️ Scraping complete! Data saved to '{OUTPUT_FILE}'{Style.RESET_ALL}")

