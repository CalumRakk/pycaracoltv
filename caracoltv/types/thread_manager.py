from pathlib import Path
import logging
import tempfile
import shutil
from threading import Thread
import threading
import re

import numpy as np

from ..utils import session
from ..constants import MAX_EXCEPTION_ATTEMPTS

logger = logging.getLogger(__name__)


exit_program = False
exit_lock = threading.Lock()

regex_segment = re.compile(r"seg-.*?\.ts")
regex_valid_filename = re.compile(r'[\\/:*?"<>|]')


def a_thread_func(part: list, folder: Path):
    global exit_program

    for index, element in enumerate(part):
        attemps = MAX_EXCEPTION_ATTEMPTS
        url = str(element)
        filename = regex_segment.search(url).group()
        path = folder.joinpath(filename)
        while attemps > 0:
            try:
                with exit_lock:
                    if exit_program:
                        exit()

                response = session.get(url, headers={})
                break
            except Exception as e:
                print(e)
                attemps -= 1

        if attemps <= 0:
            with exit_lock:
                exit_program = True
                print(
                    f"De detuvo el progrma porque el segmento ({filename}) fallo su descarga {MAX_EXCEPTION_ATTEMPTS} veces"
                )
                exit()
        path.write_bytes(response.content)
        print("\tDownloaded: ", filename, end="\r")


class ThreadManager:
    def __init__(self, playlist, video_output: Path, threads_count: int = 3):
        self.playlist = playlist
        self.threads_count = threads_count
        self.dest = video_output

    def start(self):
        self._temp_folder = Path(tempfile.mkdtemp())
        self._threads = []
        groups = np.array_split(self.playlist.files, self.threads_count)
        for index, segments in enumerate(groups, start=1):
            thread = Thread(target=a_thread_func, args=(segments, self._temp_folder))
            self._threads.append(thread)
            thread.start()

    def wait(self):
        for thread in self._threads:
            thread.join()
        self._combile_files()

    def _combile_files(self):
        if exit_program:
            logger.info(
                f"Un Hilo del ThreadManager ({self.dest}) ha fallado. Se detendrá el programa"
            )
            exit()
        else:
            logger.info(f"Combinando en {self.dest} los segmentos")
            with open(self.dest, "wb") as video:
                for segment in self.playlist.files:
                    filename = regex_segment.search(segment).group()
                    path = Path(self._temp_folder.joinpath(filename))
                    video.write(path.read_bytes())
                    path.unlink()
            shutil.rmtree(self._temp_folder)
            logger.info(f"Combinación finalizada")
