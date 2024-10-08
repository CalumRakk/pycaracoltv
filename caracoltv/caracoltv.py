from typing import Iterable
from urllib.parse import urljoin, urlparse
import requests
from lxml import etree
from . import caracoltv_utils


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

    def _get_articles(self, url, last_box=False):
        response = self._make_request(url)
        root = etree.fromstring(response.text, etree.HTMLParser())
        return caracoltv_utils.extract_articles(root, last_box=last_box)

    def _get_next_page_url(self, root):
        # Devuelve la url de la proxima paginacion (es un query como: ?0000018e-9bc4-d64b-adff-ffde258a0011-page=2)

        # En Caracol en cada pagina en la paginacion tiene varias cajas de articulos, cada una con un identificador unico.
        # La caja que más contenido carga (6 articulos) es la ultima.
        # En la siguiente imagen cada cuadro negro es una caja de articulo : https://i.imgur.com/FsLrW8B.jpeg
        url = root.find(".//meta[@property='og:url']").get("content")
        next_page_element = root.find(
            ".//*[@class='TwoColumnContainer3070']//a[@title='CARGAR MÁS']"
        )
        next_page_url = urljoin(url, next_page_element.get("data-original-href"))
        return next_page_url

    def _has_pagination_query(self, url):
        # Verifica si la url tiene el query de la paginacion
        urlparsed = urlparse(url)
        return "page=" in urlparsed.query

    def _get_query_pagination_without_index(self, url):
        # Obtiene el query sin el indice de la paginacion
        # Ejemplo: '...0000018e-9bc4-d64b-adff-ffde258a0011-page=16'
        # Devuelve: '...0000018e-9bc4-d64b-adff-ffde258a0011-page='
        urlparsed = urlparse(url)
        return urlparsed.query.split("=")[0] + "="

    def _get_pagination_url(self, url):
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

        if self._has_pagination_query(url):
            query = self._get_query_pagination_without_index(url)
            return urlparse(url)._replace(query=query).geturl()
        else:
            response = self._make_request(url)
            root = etree.fromstring(response.text, etree.HTMLParser())
            next_page_url = self._get_next_page_url(root)
            query = self._get_query_pagination_without_index(next_page_url)
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
            articles = caracoltv_utils.extract_articles(root, last_box=last_box)

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