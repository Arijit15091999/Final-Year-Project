import asyncio
import json
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

BASE_URL = "https://www.thestatesman.com/tag/stock-market/page/1"

async def main():

    browserConfig = BrowserConfig(
        headless= False,
        verbose= True,
        accept_downloads= False
    )

    # llmExtractionStrategy = LLMExtractionStrategy()

    crawlerConfig = CrawlerRunConfig(
    excluded_tags = ['header', 'footer', 'form'],
    exclude_external_links=True,
    screenshot=True,
    pdf=False,

    exclude_social_media_links= True,

    # Content processing
    process_iframes=True,
    remove_overlay_elements=True,

    # Cache control
    cache_mode=CacheMode.ENABLED,


    markdown_generator= DefaultMarkdownGenerator(),
    # Wait for a valid selector instead of setTimeout
    wait_for="document.querySelector('div.eachStory')"
)


    async with AsyncWebCrawler(config= browserConfig) as crawler:
        result = await crawler.arun(
            url = BASE_URL,
            config = crawlerConfig
        )

        if result.success:

            with open("index.md", "w", encoding = "utf-8") as file:
                file.write(result.markdown)

            # data = json.loads(result.extracted_content)
            # print(data)

            print(result.fit_markdown)

            print(result.markdown)
        else:
            print(f"Crawl failed: {result.error_message}")
            print(f"status code :- {result.status_code}")



if __name__ == "__main__":
    asyncio.run(main())