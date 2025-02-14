from scrap import getDataForYear

if __name__ == "__main__":
    index = 45292
    getDataForYear(year = 2024, startMonthIndex = 1, endMonthIndex = 12, index = index)

    index += 366

    getDataForYear(year = 2025, startMonthIndex= 1, endMonthIndex = 1, index = index)