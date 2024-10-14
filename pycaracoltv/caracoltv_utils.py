from urllib.parse import urljoin, urlparse
import requests
from lxml import etree
import json


def extract_articles(root, index=1):
    target_class = "" if index <= 1 else "//section[@class='TwoColumnContainer3070']"

    articles = []
    for element in root.xpath(f".{target_class}//*[@class='PromoB-content']"):
        string_timestamp = element.find(".//div[@data-date]").get("data-timestamp")

        title = element.find(".//h2[@class='PromoB-title']//a").text.strip()
        description = element.find(".//h3[@class='PromoB-description']//a").text.strip()
        category = element.find(".//div[@class='PromoB-title-touch']//svg/use").get(
            "xlink:href"
        )
        thumbnail = (
            element.find(".//div[@class='PromoB-media']//img")
            .get("srcset")
            .split(",")[-1]
            .split()[0]
        )
        url = element.find(".//h2[@class='PromoB-title']//a").get("href")
        timestamp = int(string_timestamp)

        articles.append(
            {
                "title": title,
                "description": description,
                "category": category,
                "thumbnail": thumbnail,
                "timestamp": timestamp,
                "url": url,
            }
        )

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
    if next_page_element is not None:
        next_page_url = urljoin(url, next_page_element.get("data-original-href"))
        return next_page_url
    return None


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


def get_pagination_from_url(url):
    """
    Obtiene la URL base de la paginación de la url, eliminando el índice de la página actual.

    Si la URL proporcionada ya contiene un query de paginación (ej. `...page=16`), se devolverá la URL con el query de paginación sin el índice,
    dejando el formato como `...page=`.

    Args:
        url (str): La URL de la cual se quiere obtener la base de la paginación.

    Returns:
        str: La URL con el query de paginación sin el índice.
    """
    query = get_query_pagination_without_index(url)
    return urlparse(url)._replace(query=query).geturl()


def get_pagination_from_root(root=None):
    """
    Obtiene la URL base de la paginación del root, eliminando el índice de la página actual.

    Returns:
        str: La URL con el query de paginación sin el índice.
    """
    url = root.find(".//meta[@property='og:url']").get("content")
    next_page_url = get_next_page_url(root)
    if next_page_url:
        query = get_query_pagination_without_index(next_page_url)
        return urlparse(url)._replace(query=query).geturl()


def make_request(url, method_head=False):
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


def get_root(url):
    response = make_request(url)
    root = etree.fromstring(response.content, etree.HTMLParser())
    response.raise_for_status()
    return root


def get_pagination_from_url_or_root(url, root):
    if has_pagination_query(url):
        return get_pagination_from_url(url)
    else:
        return get_pagination_from_root(root)


def support_section(section):
    # Verifica si la sección es de tipo capítulo o inicio
    if "capítulo" in section.lower():
        return True
    elif "inicio" in section.lower():
        return True
    else:
        return False


def extract_multimedia_data(root):
    """
    Extrae las URLs de los videos e imagenes incrustados desde varias fuentes en una página HTML.

    Esta función busca videos de YouTube, MediaStream e imagenes en carruseles (CarouselSlide) en el árbol HTML proporcionado y organiza sus URLs y metadatos en un diccionario categorizado.

    Args:
        root: Un objeto que representa el árbol del documento HTML.

    Returns:
        dict: Un diccionario con listas de URLs de videos y diapositivas. Las claves del diccionario son:
            - "youtube": Lista de URLs de videos de YouTube.
            - "mediastream": Lista de diccionarios con información de videos MediaStream, incluyendo el título del video, la URL de la playlist y las miniaturas.
            - "carousel": Lista de URLs de imágenes de carruseles (diapositivas).
    """
    videos = {"youtube": [], "mediastream": [], "carousel": []}

    # Youtube
    elements = root.xpath(".//iframe[@class='YouTubeExternalContentUrl-iframe']")
    for element in elements:
        url = element.get("src")
        videos["youtube"].append(url)

    # MediaStream HSL
    elements = root.xpath(".//ps-mediastream[@class='MediaStreamVideoPlayer']")
    for element in elements:
        data_mediastream = element.find(".//*[@data-mediastream]").get(
            "data-mediastream"
        )
        data = json.loads(data_mediastream)[0]
        video_title = element.get("data-video-title").strip()
        playlist_url = f"https://mdstrm.com/embed/{data['videoId']}"
        thumbnails = [
            value.split()[0]
            for value in element.find(".//img").get("srcset").split(",")
        ]
        videos["mediastream"].append(
            {
                "video_title": video_title,
                "playlist_url": playlist_url,
                "thumbnails": thumbnails,
                "data-mediastream": data,
            }
        )

    # CarouselSlide
    elements = root.xpath(".//div[@class='CarouselSlide-media']")
    for element in elements:
        url = element.find(".//img").get("src")
        videos["carousel"].append(url)

    return videos
