
from typing import Iterable
import requests
from lxml import etree
from . import caracoltv_utils
from urllib.parse import urljoin

class CaracolTv:

    def __init__(self):
        self._index= 1

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
            "Sec-Fetch-Dest": "document"
        }
        if method_head is True:
            return requests.head(
                url=url,
                headers=headers,
            )

        return requests.get(url=url, headers=headers)

    def get_articles(
        self, url:str
    ) -> Iterable[list[dict]]:       
        
        # En Caracol en cada pagina en la paginacion tiene varias cajas de articulos, cada una con un identificador unico.
        # La caja que más contenido carga (6 articulos) es la que tiene el identificador unknown_identifier (0011)
        # En la siguiente imagen cada cuadro negro es una caja de articulo : https://i.imgur.com/FsLrW8B.jpeg
        
        index= 1
        unknown_identifier= "0011"
        last_box=False
        while True:
            response = self._make_request(url)
            root = etree.fromstring(response.text, etree.HTMLParser())        
            
            contentId= root.find(".//meta[@name='brightspot.contentId']").get("content")
            next_page_url = f"?{contentId}{unknown_identifier}-page={index+1}"

            articles= caracoltv_utils.extract_articles(root, last_box=last_box)   
            yield {"url": url, "index": index, "articles": articles, "next_page_url": next_page_url }

            url= urljoin(url, next_page_url)
            index+= 1
            last_box= True

            if len(articles)==0:
                break
            
            


    
        


        # url= root.find(".//meta[@property='og:url']").get("content")
        # next_page_element= root.find(".//*[@class='TwoColumnContainer3070']//a[@title='CARGAR MÁS']")        
        # next_page_url = urljoin(url, next_page_element.get("data-original-href"))
