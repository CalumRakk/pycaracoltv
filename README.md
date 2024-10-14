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
URL = "https://www.caracoltv.com/desafio/capitulos/capitulo-114-desafio-20-anos-kevyn-y-darlyn-se-disputan-la-gran-final-con-sus-refuerzos-pr30"

data = caracol.get_page(URL)
# Imprimir los datos parseados
print(data["parsed_data"])
```

### Salida esperada

El código anterior devolverá un JSON con una estructura parecida a la siguiente:

```json
{
  "title": "Capítulo final Desafío 20 Años: Kevyn y Darlyn se disputan la gran final con sus refuerzos",
  "description": "Al Box Negro llegan los dos finalistas que se enfrentan en la última prueba para coronarse como campeones del Desafío 20 Años.",
  "img": "https://caracoltv.brightspotcdn.com/images/capitulo-final-desafio-20-anos.jpg",
  "img_alt": "Capítulo 114 Desafío 20 Años",
  "multimedia": {
    "youtube": [],
    "mediastream": [],
    "carousel": []
  }
}
```

## Ejemplo: Extraer todos los capítulos de una serie

Este ejemplo muestra cómo utilizar `pycaracoltv` para obtener la lista completa de capítulos de una serie desde Caracol TV y extraer el título y el enlace del video de cada uno:

```python
from pycaracoltv import CaracolTv

caracol = CaracolTv()
URL = "https://www.caracoltv.com/desafio/capitulos"

# Recorrer todos los artículos de la página
for page_article in caracol.get_articles(URL):
    for article in page_article["articles"]:

        page_video = caracol.get_page(article["url"])
        data_parse = page_video["parsed_data"]

        title = data_parse["title"]
        video = data_parse["multimedia"]["mediastream"][0]["playlist_url"]

        print(title, video)
```

### Salida esperada

El código anterior imprimirá en la consola el título y el enlace de cada video de los capítulos disponibles:

```shell
Capítulo 113 Desafío 20 Años: En el Desafío de los Favoritos se entregan 200 millones de pesos https://mdstrm.com/embed/66f60860d7ec1c0e1aa0da36
Capítulo 112 Desafío 20 Años: El Desafío Final define a los dos grandes finalistas del reality https://mdstrm.com/embed/66f4b744ad3a9484990822fd
Capítulo 111 Desafío 20 Años: ¿El último Desafío a Muerte se presta para una reconciliación? https://mdstrm.com/embed/66f366c76d32a79f1290c570
Capítulo 110 Desafío 20 Años: Segundo Duelo de Salvación: ¿Algún Tino pasa al Desafío Final? https://mdstrm.com/embed/66f21e9ad29c5a77d52c9aff
Capítulo 109 Desafío 20 Años: Inician los duelos por parejas y vuelven los Brazaletes de Salvación https://mdstrm.com/embed/66ee1e6cf6144bb48ea5ffb2
```
