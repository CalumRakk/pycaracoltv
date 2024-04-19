from urllib.parse import urljoin
import re

import requests
from lxml import etree

from .base import Base
from .article import Article


class Serie(Base):
    def __init__(self, url: str) -> None:
        self.url = url

        self._index = 7

    @property
    def index(self):
        return getattr(self, "_index")

    @property
    def pagination_code(self):
        if hasattr(self, "_pagination_code") is False:
            article = self.root.xpath(".//a[@title='CARGAR MÁS']")[-1]
            code = article.get("href").split("=")[0]
            setattr(self, "_pagination_code", code)
        return getattr(self, "_pagination_code")

    def next_page(self):
        url_next_page = (
            urljoin(self.url, self.pagination_code) + "=" + str(self.index + 1)
        )
        response = requests.get(url_next_page)
        root = etree.fromstring(response.content, etree.HTMLParser())
        setattr(self, "_root", root)
        setattr(self, "_index", self.index + 1)

    def extract_articles_from_main_element(self, main_element):
        articles = []
        for element in main_element.xpath(".//*[@class='PromoB-content']"):
            a_article = element.find(".//a[@class='Link']")
            a_serie = element.find(".//div[@class='PromoB-category-touch']/a")

            url = a_article.get("href")
            title = a_article.get("title")
            thumbnail = a_article.find(".//img").get("data-src")

            number = int(re.search(r"Capítulo (\d+)", title).group(1))

            data_timestamp = element.find(".//div[@data-date]").get("data-timestamp")

            serie_name = a_serie.get("title")
            serie_url = a_serie.get("href")
            article = Article(
                url=url,
                title=title,
                thumbnail=thumbnail,
                number=number,
                data_timestamp=data_timestamp,
                serie_name=serie_name,
                serie_url=serie_url,
            )
            articles.append(article)
        return articles

    def _extract_articles(self):
        if self.index == 0:
            return self.extract_articles_from_main_element(self.root)
        else:
            xpath = "//li[@class='TwoColumnContainer3070-column' and @item-columntwo]"
            last_column = self.root.xpath(xpath)
            if last_column:
                last_column = last_column[0]
                return self.extract_articles_from_main_element(last_column)

    def iter_chapter_articles(self):
        articles = self._extract_articles()
        while bool(articles):
            self.next_page()
            articles = self._extract_articles()
            yield articles
