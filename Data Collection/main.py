from ET_data_scrap import getDataForYear
from ET_get_text import getNewsFromLink
from ET_get_news_data_modified import scrape_news
from multiprocessing import cpu_count

if __name__ == "__main__":
    # getDataForYear(
    #     year=2023,
    #     startMonthIndex=1,
    #     endMonthIndex=12,
    #     index = 44927
    # )

    # getNewsFromLink()
    # scrape_news()
    print(cpu_count())