
from datetime import datetime

class TvShow:
    def __init__(self, title, source_time) -> None:
        self.title = title or ""
        self.source_time = source_time
        self.start_time = source_time.split(" - ")[0]
        self.end_time = source_time.split(" - ")[1]

    def get_start_time(self):
        now_string = datetime.now().strftime("%d-%m-%y")
        return datetime.strptime(f"{now_string} {self.start_time}", "%d-%m-%y %I:%M %p")

    def get_end_time(self):
        now_string = datetime.now().strftime("%d-%m-%y")
        return datetime.strptime(f"{now_string} {self.end_time}", "%d-%m-%y %I:%M %p")

    def __str__(self) -> str:
        return (
            self.title + " - " + datetime.now().strftime("%d-%m-%y ") + self.source_time
        )

    def dirname(self):
        title = self.title.replace(" ", "_")
        time_ = self.source_time.replace(" ", "").replace(":", ".")
        return f"{self.title}_{datetime.now().strftime('%d-%m-%y')}_{time_}"
