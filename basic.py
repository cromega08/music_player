from pytube import YouTube as yt
from playsound import playsound as ps
import os

current = os.getcwd()

download_dir = os.path.join(current, ".downloads")

if os.path.exists(download_dir) == False:

    os.mkdir()

url = "https://music.youtube.com/watch?v=GtPLYvYeZ_4&feature=share"

video = yt(url)

stream = video.streams.first()

stream.download(output_path=download_dir)

print(f"{video.title} was downloaded")

for dirs in os.listdir(download_dir): print(dirs)