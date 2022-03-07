import mimetypes
from pytube import YouTube as yt
from playsound import playsound as ps
from bs4 import BeautifulSoup as bs
import os

class started():

    def __init__(self):
        
        self.current = os.getcwd()

    def check_download_dir(self):

        download_dir = os.path.join(self.current, ".downloads")

        if os.path.exists(download_dir) == False:

            os.mkdir(download_dir)

class downloads():

    def __init__(self, url, download_dir):

        self.url = url
        self.download_dir = download_dir

    def download_stream(self):

        video = yt(self.url)

        stream = video.streams.first()

        stream.download(output_path=self.download_dir)

        stream.includes_audio_track

        video_suffix = bs(stream.get_file_path).get(mimetypes)

        self.output(f"{video.title}.{video_suffix}")

    def output(self, video_filepath=str):
        
        print(f"{video_filepath} was downloaded")
        

url = "https://music.youtube.com/watch?v=GtPLYvYeZ_4&feature=share"

class player():

    def __init__(self, download_dir):
        
        self.download_dir = download_dir

        for music in os.listdir(download_dir): print(music)