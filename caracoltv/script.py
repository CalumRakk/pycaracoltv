#
import m3u8
import threading
from typing import List

from .utils import ejecutar_tarea, get_master, check_resolutions


def run(folder, resolutions):
    master = get_master()
    check_resolutions(master, resolutions)
    segments_descargados = []
    hilos = []
    for resolution in resolutions:
        hilo = threading.Thread(
            target=ejecutar_tarea,
            args=(
                folder,
                master,
                resolution,
                segments_descargados,
            ),
        )
        hilos.append(hilo)

    for hilo in hilos:
        hilo.start()


def download_episode(url: str, episode_number: str):
    serie = Serie(url)
    for page in serie.page_episodes():
        article_episodes = page.episodes()
        for article_episode in article_episodes:
            if article_episode.episode_number == episode_number:
                episode = article_episode.get_episode()

                if episode.path.exists():
                    print(f"Existe: {episode.path}")
                    continue

                episode.download()
