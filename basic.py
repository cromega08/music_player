from ast import match_case
from pytube import YouTube as yt
import sounddevice as sd
import soundfile as sf
import os

class started():

    def __init__(self):
        
        self.current = os.getcwd()

    def check_download_dir(self):

        download_dir = os.path.join(self.current, ".downloads")

        if os.path.exists(download_dir) == False:

            os.mkdir(download_dir)

        return download_dir

class downloader():

    def __init__(self, url, download_dir):

        self.url = url
        self.download_dir = download_dir

    def download_stream(self):

        video = yt(self.url)

        stream = video.streams.first()

        stream.download(output_path=self.download_dir)

        video_suffix = stream.subtype

        self.output(f"{video.title}.{video_suffix}")

    def output(self, video_filepath=str):
        
        print(f"{video_filepath} was downloaded")
        
class player():

    def __init__(self, download_dir):
        
        self.download_dir = download_dir
        self.music = os.listdir(self.download_dir)

    def songs_listed(self):

        for songs in self.music: print(f"{self.music.index(songs)+1}. {songs}")

        choose = input("Song number: ")

        assert choose.isnumeric

        return int(choose)-1

    def play(self, song_number=int):

        song = self.music[int(song_number)]

        fr, sr= sf.read(f"{self.download_dir}/{song}")
        sd.play(fr, sr,)

class app():

    def __init__(self):

        first = started()
        
        self.current = first.current
        self.download_dir = first.check_download_dir()

    def exec(self):

        url = int(input("1. Play music downloaded\n2. Download music from YouTube\n\nOption: "))
        
        match url:

            case 1:

                sound = player(self.download_dir)

                song = sound.songs_listed()

                sound.play(song)

            case 2:

                url = input("URL: ")

                downloads = downloader(url, self.download_dir)

                downloads.download_stream()


app().exec()