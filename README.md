`pycaracoltv` es una herramienta de **web scraping** para extraer videos, imágenes y otros tipos de metadatos de la página [caracoltv.com](https://www.caracoltv.com).

## Instalación

Instala la librería utilizando `pip`:

```bash
pip install pycaracoltv
```

## Uso básico

A continuación, un ejemplo de uso para obtener los datos de una página de Caracol TV:

```python
from pycaracoltv import CaracolTv

caracol = CaracolTv()
URL = "https://www.caracoltv.com/desafio/capitulos/capitulo-32-completo-desafio-20-anos-un-equipo-intenta-darle-de-baja-a-su-capitan-pr30"

article_data = caracol.get_article(URL)
title= article_data["video"]["name"]
url= article_data["video"]["embedUrl"]
print(title, url)

# Resultado:
# Un equipo intenta darle de baja a su capitán- Capítulo 32 - Desafío XX https://www.youtube.com/embed/p02EW3isVIo
```

## Ejemplo: Extraer todos los capítulos de una serie

Este ejemplo muestra cómo utilizar `pycaracoltv` para obtener la lista completa de capítulos de una serie desde Caracol TV y extraer el título y el enlace del video de cada uno:

```python
from pycaracoltv import CaracolTv

caracol = CaracolTv()
URL = "https://www.caracoltv.com/desafio/capitulos"

# Recorrer todos los artículos de la página
for page_data in caracol.get_articles(URL):
    for article in page_data["articles"]:
        article_data = caracol.get_article(article["url"])

        title= article_data["video"]["name"]
        embedUrl= article_data["video"]["embedUrl"]
        print(title, embedUrl,"\n")
```

### Salida esperada

El código anterior imprimirá en la consola el título y el enlace de cada video de los capítulos disponibles:

```shell
Capítulo 113 Desafío 20 Años: En el Desafío de los Favoritos se entregan 200 millones de pesos |Desafío XX https://mdstrm.com/embed/66f60860d7ec1c0e1aa0da36

Capítulo 112 Desafío 20 Años: El Desafío Final define a los dos grandes finalistas del reality https://mdstrm.com/embed/66f4b744ad3a9484990822fd

¿El Último Desafío a Muerte se presta para una reconciliación o más rencor? Capítulo 111 |Desafío XX https://mdstrm.com/embed/66f366c76d32a79f1290c570

¿Algún Tino pasa al Desafío Final o competirán entre ellos en Muerte? –Capítulo 110 |Desafío XX https://mdstrm.com/embed/66f21e9ad29c5a77d52c9aff

...
```
