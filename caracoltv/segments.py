
import csv
import os
from .utils import HEADERS, get_filename, session
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .folder import Folder

class Segments:
    def __init__(self, folder: 'Folder') -> None:
        self.folder = folder

        self.dirname = "segments"
        self.filename = "segments.csv"
        self.path_csv = os.path.join(
            folder.path, self.filename
        )  # path del archivo csv que guarda un registro de segmentos.

    @property
    def class_name(self):
        return self.__class__.__name__

    def __getattr__(self, attr):
        class_name = self.class_name
        # Se añade adelante el nombre de la clase para que el nombre de los atributos encaje con el enmascaramiento de nombre natural de Python
        if f"_{class_name}__files" == attr:
            files = []
            if os.path.exists(self.path_csv):
                with open(self.path_csv, newline="") as archivo_csv:
                    lector_csv = csv.DictReader(archivo_csv)
                    for fila in lector_csv:
                        files.append(fila)
            setattr(self, attr, files)
            return self.__dict__[attr]
        elif f"_{class_name}__filenames" == attr:
            filenames = [file["filename"] for file in self.files]
            setattr(self, attr, filenames)
            return self.__dict__[attr]
        elif f"_{class_name}__path" == attr:
            path = os.path.join(
                self.folder.path, self.dirname
            )  # carpeta donde se guardan los segmentos
            if not os.path.exists(path):
                os.makedirs(path)
            setattr(self, attr, path)
            return self.__dict__[attr]

    @property
    def path(self):
        class_name = self.__class__.__name__
        return getattr(self, f"_{class_name}__path")

    @property
    def files(self) -> list:
        class_name = self.__class__.__name__
        return getattr(self, f"_{class_name}__files")

    @property
    def filenames(self) -> list:
        class_name = self.__class__.__name__
        return getattr(self, f"_{class_name}__filenames")

    def exists(self, segment):
        filename = get_filename.search(segment.uri).group()
        return filename in self.filenames

    def add(self, segment):
        url = segment.uri
        filename = get_filename.search(url).group()

        path = os.path.join(self.path, filename)

        response = session.get(url, headers=HEADERS)
        with open(path, "wb") as f:
            f.write(response.content)

        file = {"filename": filename, "url": url}
        self.files.append(file)
        self.filenames.append(file["filename"])
        return file

    def save(self):
        with open(self.path_csv, "w", newline="") as archivo_csv:
            campos = ["filename", "url"]
            escritor_csv = csv.DictWriter(archivo_csv, fieldnames=campos)

            escritor_csv.writeheader()
            rows = [
                {"filename": row["filename"], "url": row["url"]} for row in self.files
            ]
            escritor_csv.writerows(rows)

    def save_segments(self, segments):
        pass

    def __str__(self) -> str:
        return self.path

    def _download_segment(self, url, path):
        response = session.get(url, headers=HEADERS)
        with open(path, "wb") as f:
            f.write(response.content)
            return True
