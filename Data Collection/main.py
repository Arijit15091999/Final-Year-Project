from ET_data_scrap import getDataForYear
from ET_get_text import getNewsFromLink
from Bs4_article_scrape import scrape_news
from multiprocessing import cpu_count
from get_mw4me_news import get_article_info, kill_all_instances_of_firefox_and_geckodriver
from colorama import Style, Fore

if __name__ == "__main__":
    try:
        # Start with a clean slate
        kill_all_instances_of_firefox_and_geckodriver()
        
        # Run the scraper
        get_article_info()
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}\nScript interrupted by user{Style.RESET_ALL}")
    finally:
        kill_all_instances_of_firefox_and_geckodriver()
        print(f"{Fore.GREEN}Script completed. All browser instances cleaned up.{Style.RESET_ALL}")