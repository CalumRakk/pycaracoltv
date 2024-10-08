from typing import Iterable
import requests
from lxml import etree
from . import caracoltv_utils as utils
from urllib.parse import urljoin, urlparse

class CaracolTv:

    def __init__(self):
        self._index = 1

    @property
    def index(self):
        return getattr(self, "_index")

    def _make_request(self, url, method_head=False):
        headers = {
            "sec-ch-ua": '"Chromium";v="118", "Brave";v="118", "Not=A?Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Sec-GPC": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
        }
        if method_head is True:
            return requests.head(
                url=url,
                headers=headers,
            )

        return requests.get(url=url, headers=headers)
    
    def _get_pagination_url(self,url):
        """
        Obtiene la URL base de la paginación, eliminando el índice de la página actual.

        Si la URL proporcionada ya contiene un query de paginación (ej. `...page=16`), se devolverá la URL con el query de paginación sin el índice,
        dejando el formato como `...page=`.

        Si la URL no contiene un query de paginación, se hace una solicitud a la página para obtener la URL de la siguiente página, y se formatea de la misma manera eliminando el índice de la paginación.

        Args:
            url (str): La URL de la cual se quiere obtener la base de la paginación.

        Returns:
            str: La URL con el query de paginación sin el índice.
        """

        if utils.has_pagination_query(url):
            query = utils.get_query_pagination_without_index(url)
            return urlparse(url)._replace(query=query).geturl()
        else:
            response = self._make_request(url)
            root = etree.fromstring(response.text, etree.HTMLParser())
            next_page_url = utils.get_next_page_url(root)
            query = utils.get_query_pagination_without_index(next_page_url)
            return urlparse(url)._replace(query=query).geturl()
    
    def get_articles(self, url: str, start_index: int = 1) -> Iterable[list[dict]]:
        index = 1
        last_box = False
        pagination_url = self._get_pagination_url(url)

        if start_index != 1:
            index = start_index
            url = pagination_url + str(index)
            next_page_url = pagination_url + str(index + 1)
            last_box = True

        while True:
            response = self._make_request(url)
            root = etree.fromstring(response.text, etree.HTMLParser())
            articles = utils.extract_articles(root, last_box=last_box)

            next_page_url = pagination_url + str(index + 1)
            if len(articles) == 0:
                break
            
            yield {
                "url": url,
                "index": index,
                "articles": articles,
                "next_page_url": next_page_url,
            }

            url = next_page_url
            index += 1
            last_box = True