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
            last_box = True

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

    def get_page(self, url):
        """
        Extrae y devuelve los datos clave de una página de CaracolTV, junto con su contenido HTML sin procesar.

        Args:
            url (str): La URL de la página.

        Returns:
            dict: Un diccionario que contiene dos campos:
                - 'parsed_data': Un diccionario con los datos extraídos de la página, que incluye:
                    - 'title' (str): El título del artículo.
                    - 'description' (str): La descripción o subtítulo del artículo.
                    - 'img' (str): La URL de la imagen principal del artículo.
                    - 'img_alt' (str): El texto alternativo de la imagen principal.
                    - 'multimedia' (list): Lista de contenido multimedia extraído de la página.
                - 'raw_html' (str): El contenido HTML sin procesar de la página.
        """
        response = utils.make_request(url)
        root = html.fromstring(response.text)

        article_element = root.find(".//div[@class='ArticlePage-content']")
        title = article_element.find(".//h1").text.strip()
        drescription = article_element.find(".//h2").text.strip()
        img = article_element.find(".//img").get("srcset").split(",")[-1].split()[0]
        img_alt = article_element.find(".//img").get("alt")
        multimedia = utils.extract_multimedia_data(root)
        return {
            "parsed_data": {
                "title": title,
                "description": drescription,
                "img": img,
                "img_alt": img_alt,
                "multimedia": multimedia,
            },
            "raw_html": response.text,
        }
