from urllib.parse import urlparse, urljoin
from pathlib import Path
import requests
from lxml import etree


class MainPage:
    def __init__(self, url: str) -> None:
        self.url = url

    # def __init__(self, url: str) -> None:
    #     self.url_main_serie = self.__get_url_main_serie(url)

    # @property
    # def url_chapter_articles(self):
    #     return (self.url_main_serie, "capitulos")

    # def __get_url_main_serie(self, url):
    #     parse = urlparse(url)
    #     path = Path(parse.path)
    #     url_base = f"{parse.scheme}://{parse.hostname}/"
    #     return urljoin(base=url_base, url=path.parts[1])

    def iter_chapter_articles(self):
        response = requests.get(self.url)

        root = etree.fromstring(response.content, etree.HTMLParser())
        Path("indext.html").write_text(response.text)
        for data_container in root.xpath("//*[@data-container]"):
            items = data_container.xpath(".//li")
            for item in items:
                pass
        print(response)
