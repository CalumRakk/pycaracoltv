from typing import Iterable
from . import caracoltv_utils as utils
from lxml import html
import json

class CaracolTv:
    def get_articles(self, url: str, start_index: int = 1) -> Iterable[list[dict]]:
        index = 1
        root = utils.get_root(url)
        section = root.find(".//li[@data-current-nav-item]//a").text

        if utils.support_section(section) is False:
            raise ValueError(f"La URL no es compatible:  {url}")

        pagination_url = utils.get_pagination_from_url_or_root(url, root)
        next_page_url = None

        if start_index != 1:
            index = start_index
            url = pagination_url + str(index)
            next_page_url = pagination_url + str(index + 1)

        while True:
            articles = utils.extract_articles(root, index=index)
            next_page_url = pagination_url + str(index + 1) if pagination_url else None

            if len(articles) == 0:
                break

            yield {
                "url": url,
                "index": index,
                "articles": articles,
                "next_page_url": next_page_url,
                "section": section,
            }

            index += 1
            if next_page_url:
                root = utils.get_root(next_page_url)
            else:
                break

    def get_article(self, url)->dict:
        """
        Extrae y devuelve los datos clave de una página de CaracolTV, junto con su contenido HTML sin procesar.
        Args:
            url (str): La URL de la página.
        """
        response = utils.make_request(url)
        root = html.fromstring(response.text)
        
        json_data= utils.extract_news_articles(root)
        json_data.update({"raw_html": response.text})
        return  json_data
