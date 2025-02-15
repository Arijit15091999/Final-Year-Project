from selenium import webdriver
from selenium.webdriver.common.by import By
from colorama import Fore, Style, init


init(autoreset=True)

link = "https://economictimes.indiatimes.com/news/india/asi-seeks-shahi-jama-masjids-control-files-reply-in-court/articleshow/115873714.cms"

def getNewsTextFromLink(link):
    try:
        driver = webdriver.Firefox()
        print(f"{Fore.CYAN}Fetching data from: {link}{Style.RESET_ALL}")

        driver.get(
            url = link
        )

        if "access denied" in str.lower(driver.find_element(by = By.TAG_NAME, value = "h1").text):
            print(f"{Fore.YELLOW}⚠️ No news found {Style.RESET_ALL}")
        else:
            scripts = """
                document.getElementById("sr_widget").remove();
                Array.from(
                    document.getElementsByClassName('growfast_widget'))
                    .forEach(e => e.remove());
                """
            driver.execute_script(script=scripts)
            articleText = driver.find_element(
                by = By.CLASS_NAME,
                value = "artText"
            )
            print(articleText.text)
    # except:
    #     print(f"{Fore.YELLOW}⚠️ No news found {Style.RESET_ALL}")
    finally:
        driver.quit()


getNewsTextFromLink(link = link)
