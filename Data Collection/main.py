from ET_data_scrap import getDataForYear
from ET_get_text import getNewsFromLink
from ET_get_news_data_modified import scrape_news
from multiprocessing import cpu_count

if __name__ == "__main__":
    index = 39448
    start_year = 2008
    end_year = 2022
    
    for year in range(start_year, end_year + 1):
        getDataForYear(
            year = year,
            startMonthIndex=1,
            endMonthIndex=12,
            index=index
        )
        
        if(year % 4 == 0):
            index = index + 366
        else:
            index = index + 365

    # print(f"CPU COUNT = {cpu_count()}")
    # scrape_news()