
from datetime import datetime


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

# def extract_articles(root):
#     xpath = "//li[@class='TwoColumnContainer3070-column' and @item-columntwo]"
#     last_box = .root.xpath(xpath)
#     if last_box:
#         last_box = last_box[0]
#         return .extract_articles_from_main_element(last_box)

# def iter_chapter_articles() -> Generator[list[Article], None, None]:
#     """
#     Genera y devuelve artículos de capítulos de forma iterativa.

#     Este método extrae los artículos de capítulos de la página actual y los devuelve.
#     Luego, avanza a la siguiente página y continúa extrayendo artículos hasta que no haya más.

#     Yields:
#         list[Article]: Una lista de objetos de artículo de capítulo.
#     """

#     articles = ._extract_articles()
#     yield articles
#     while bool(articles):
#         .next_page()
#         articles = ._extract_articles()
#         yield articles
