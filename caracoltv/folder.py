
from .segments import Segments

class Folder:
    def __init__(self, path):
        self.path = path

    @property
    def segments(self):
        attr = "__segments"
        if hasattr(self, attr) is False:
            setattr(self, attr, Segments(self))
        return getattr(self, attr)

    def __str__(self) -> str:
        return self.path

