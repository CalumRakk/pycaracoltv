from pytube import Channel
from datetime import datetime
import re

def searcherYouTube():
    c = Channel("https://www.youtube.com/channel/UCXfuQ0yx-p2Q_ST9zFNbx_g/videos")

    regex= re.compile("Capítulo \d|Capítulo\d", re.IGNORECASE)

    for video in c.videos:
        if datetime.now().day== video.publish_date.day:
            if regex.search(video.title):
                filename= f"{regex.search(video.title).group()} HD - Desafío The Box 2022.mp4"
                print("Downloading...", filename)                
                stream = video.streams.get_by_itag(22)
                stream.download(filename=filename)
                
                filename= f"{regex.search(video.title).group()} SD - Desafío The Box 2022.mp4"
                print("Downloading...", filename)
                stream= video.streams.get_by_itag(135)
                stream.download(filename=filename)
                return True
            continue
        return False