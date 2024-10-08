
from datetime import datetime
from urllib.parse import urljoin, urlparse

def extract_articles(root, last_box=False):
    target_class= "" if not last_box else "//section[@class='TwoColumnContainer3070']"

    articles = []
    for element in root.xpath(f".{target_class}//*[@class='PromoB-content']"):
        string_timestamp = element.find(".//div[@data-date]").get("data-timestamp")

        title= element.find(".//h2[@class='PromoB-title']//a").text.strip()
        description= element.find(".//h3[@class='PromoB-description']//a").text.strip()
        category= element.find(".//div[@class='PromoB-title-touch']//svg/use").get("xlink:href")
        thumbnail= element.find(".//div[@class='PromoB-media']//img").get("src")
        timestamp= int(string_timestamp)

        articles.append({
            "title": title,
            "description": description,
            "category": category,
            "thumbnail": thumbnail,
            "timestamp": timestamp
            })
        
    return articles


def get_next_page_url(root):
    """
    Obtiene la URL de la próxima página de paginación a partir de un documento HTML.
    """
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

def has_pagination_query(url):
    """
    Verifica si una URL contiene un query de paginación.

    Esta función analiza la URL y determina si incluye un parámetro `page=` en su query, lo que indica la presencia de paginación.

    Args:
        url (str): La URL que se va a verificar.

    Returns:
        bool: True si la URL contiene el query de paginación (`page=`), False en caso contrario.
    """
    # Verifica si la url tiene el query de la paginacion
    urlparsed = urlparse(url)
    return "page=" in urlparsed.query

def get_query_pagination_without_index(url):
    """
    Extrae el query de paginación de una URL, eliminando el índice de la página actual.

    Esta función toma una URL que contiene un query de paginación (ej. `page=16`) y devuelve el query sin el índice de la página, dejando el formato como `page=`.

    Args:
        url (str): La URL de la cual se desea extraer el query de paginación.

    Returns:
        str: El query de paginación sin el índice, con el formato `page=`.
    """
    # Obtiene el query sin el indice de la paginacion
    # Ejemplo: '...0000018e-9bc4-d64b-adff-ffde258a0011-page=16'
    # Devuelve: '...0000018e-9bc4-d64b-adff-ffde258a0011-page='
    urlparsed = urlparse(url)
    return urlparsed.query.split("=")[0] + "="


