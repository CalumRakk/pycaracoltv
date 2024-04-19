from urllib import parse
from .base import Base


class URL_Identifier(Base):
    def __init__(self, url: str) -> None:
        self.url = url

    @property
    def is_video(self):
        if hasattr(self, "_is_video") is False:
            setattr(self, "_is_video", self._identifier())
        return getattr(self, "_is_video")

    def _identifier(self):
        """Devuelve True si la URL es un episode"""
        # Para identificar si la url es de una serie o de un episodio, se busca el @type = NewsArticle en los jsons,
        # Si existe es porque estamos ante una URL de episodio.

        for data in self.jsons:
            if data["@type"] == "NewsArticle":
                return True
        return False

    def get_serie(self):
        # Para encontrar la serie en los jsons. hay que identificar primero el @type = BreadcrumbList
        # y luego buscar en sus items el item que la URL item tenga un path un padre.
        for data in self.jsons:
            if data["@type"] == "BreadcrumbList":
                for item in data["itemListElement"]:
                    urlparsed = parse.urlparse(item["item"])
                    if urlparsed.path.count("/") == 1:
                        return item["item"]
