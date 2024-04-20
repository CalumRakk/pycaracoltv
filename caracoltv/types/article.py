from datetime import datetime


class Article:
    def __init__(
        self,
        url: str,
        title: str,
        thumbnail: str,
        number: int,
        data_timestamp: str,
        serie_name: str,
        serie_url: str,
    ) -> None:
        self.url = url
        self.title = title.strip()
        self.thumbnail = thumbnail
        self.number = number
        self.data_timestamp = data_timestamp
        self.serie_name = serie_name.strip()
        self.serie_url = serie_url

    @property
    def pub_date(self):
        return datetime.fromtimestamp(int(self.data_timestamp))

    def visit_chapter_page():
        pass

    def to_dict(self):
        return {
            "url": self.url,
            "title": self.title,
            "thumbnail": self.thumbnail,
            "number": self.number,
            "data_timestamp": self.data_timestamp,
            "serie_name": self.serie_name,
            "serie_url": self.serie_url,
        }
