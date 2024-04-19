import json

from lxml import etree
import requests


class Base:
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
