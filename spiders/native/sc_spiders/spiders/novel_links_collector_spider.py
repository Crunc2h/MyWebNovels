import os
from fake_useragent import UserAgent
from scrapy import signals
import scrapy

UA = UserAgent()

BASE_LINK_TEST = "https://www.webnovelpub.pro"


class WebnovelpubNovelLinksCollector(scrapy.Spider):
    name = "webnovelpub__links_collector"
    custom_settings = {"USER_AGENT": UA.chrome}
    file_str = "sc_spiders/extracted_data/webnovelpub/links.txt"
    current_page = 1
    max_page = 0

    def start_requests(self):
        if os.path.exists(self.file_str):
            with open(self.file_str, "w") as f:
                f.write("")
        urls = [
            "https://www.webnovelpub.pro/browse/genre-all-25060123/order-new/status-all",
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if self.max_page == 0:
            self.max_page = int(
                response.css(".PagedList-skipToLast > a:nth-child(1)::attr(href)")
                .get()
                .split("page=")[1]
            )
        print(f"------------------------------------->{self.max_page}")
        print(f"------------------------------------->{self.current_page}")
        novels_on_page = response.css("li.novel-item a::attr(href)").getall()
        with open(self.file_str, "a") as file:
            file.write("\n".join(novels_on_page))

        next_page = response.css(
            ".PagedList-skipToNext > a:nth-child(1)::attr(href)"
        ).get()
        if next_page is not None:
            self.current_page += 1
            yield response.follow(next_page, self.parse)
        else:
            if self.current_page != self.max_page:
                print("WWWWWWWWWWWWWWWWTTTTTTTTTTTTTTTTTTTTTFFFFFFFFFFFFFFFFFFFFF")

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        print("test")
        spider = super(WebnovelpubNovelLinksCollector, cls).from_crawler(
            crawler, *args, **kwargs
        )
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        with open(spider.file_str, "r") as file:
            restructured = "".join(
                list(
                    map(
                        lambda link: BASE_LINK_TEST + link + "\n",
                        set(file.read().split("\n")),
                    )
                )
            )
        with open(spider.file_str, "w") as file:
            file.write(restructured)
