import json
from urllib.parse import urlparse

from lxml import etree
import requests


class Base:
    @property
    def serie_articles_url(self):
        if hasattr(self, "_serie_articles_url") is False:
            serie_articles_url = self._get_serie_articles_url(self.jsons)
            setattr(self, "_serie_articles_url", serie_articles_url)
        return getattr(self, "_serie_articles_url")

    @property
    def serie_homepage_url(self):
        if hasattr(self, "_serie_homepage_url") is False:
            serie_homepage_url = self._get_serie_homepage_url(self.jsons)
            setattr(self, "_serie_homepage_url", serie_homepage_url)
        return getattr(self, "_serie_homepage_url")

    @property
    def root(self) -> "etree":
        """
        Devuelve la raíz de un árbol XML utilizando la biblioteca lxml en Python.

        Si la raíz aún no ha sido almacenada en la instancia de la clase, realiza una solicitud HTTP
        a una URL especificada para obtener el contenido XML. Luego, procesa este contenido para crear
        un árbol XML utilizando la biblioteca lxml. La raíz del árbol XML se almacena en la instancia
        de la clase para un acceso futuro más rápido.

        Returns:
            etree.Element: La raíz del árbol XML.

        """
        if hasattr(self, "_root") is False:
            response = requests.get(self.url)
            root = etree.fromstring(response.content, etree.HTMLParser())
            setattr(self, "_root", root)

        return getattr(self, "_root")

    @property
    def jsons(self):
        """
        Extrae y devuelve todos los objetos JSON incrustados del tipo 'application/ld+json'
        presentes en el contenido XML del árbol.

        Hace uso de cache en memoria para un uso más optimo.

        Returns:
            list: Una lista que contiene todos los objetos JSON extraídos del contenido XML.

        """
        if hasattr(self, "_jsons") is False:
            data_list = []
            for script_node in self.root.xpath("//script[@type='application/ld+json']"):
                data = json.loads(script_node.text)
                data_list.append(data)
            setattr(self, "_jsons", data_list)
        return getattr(self, "_jsons")

    @property
    def is_video(self):
        """Devuelve True si el root actual contiene un video"""
        for data in self.jsons:
            if data["@type"] == "NewsArticle":
                return True
        return False

    def _get_serie_homepage_url(self, jsons: list[dict]) -> str:
        """
        Obtiene la URL de la página principal de la serie a partir de una lista de objetos JSON.

        Esta función busca entre los objetos JSON una lista de elementos de tipo BreadcrumbList (@type) que representan
        la estructura de navegación de la serie. Luego, analiza cada elemento de la lista en busca de una URL. Si encuentra
        una URL con una ruta que contiene exactamente un segmento, se deduce que es la URL de la página principal de la serie
        y la devuelve.

        Args:
            jsons (list[dict]): Una lista de objetos JSON que contienen información de la serie.

        Returns:
            str: La URL de la página principal de la serie.

        Raises:
            Exception: Si no se encuentra la URL de la página principal de la serie.
        """
        for data in jsons:
            if data["@type"] == "BreadcrumbList":
                for item in data["itemListElement"]:
                    urlparsed = urlparse(item["item"])
                    if urlparsed.path.count("/") == 1:
                        return item["item"]
        raise Exception("Serie homepage URL not found")

    def _get_serie_articles_url(self, jsons: list[dict]) -> str:
        """
        Obtiene la URL de los artículos (episodios) de la serie a partir de una lista de objetos JSON.

        Esta función busca entre los objetos JSON una lista de elementos de tipo BreadcrumbList (@type) que representan
        la estructura de navegación de la serie. Luego, analiza cada elemento de la lista en busca de una URL. Si encuentra
        una URL con una ruta que contiene exactamente dos segmentos, se deduce que es la URL de los artículos y la devuelve.
        En caso contrario, se asume que la URL de los artículos es la misma que la URL de la página principal de la serie
        (serie_homepage_url).

        Args:
            jsons (list[dict]): Una lista de objetos JSON que contienen información de la serie.

        Returns:
            str: La URL de los artículos (episodios) de la serie.
        """

        for data in jsons:
            if data["@type"] == "BreadcrumbList":
                for item in data["itemListElement"]:
                    urlparsed = urlparse(item["item"])
                    if urlparsed.path.count("/") == 2:
                        return item["item"]
        return self.serie_homepage_url
