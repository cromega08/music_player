#GPL-3.0-or-later

from ast import match_case
from genericpath import isdir, isfile
from pytube import YouTube as yt
import sounddevice as sd
import soundfile as sf
import pydub as pd
import requests
import os

class started():

    def __init__(self):
        
        self.current = os.getcwd()
        self.download_dir = self.check_download_dir()
        self.op_system = os.name

    def check_download_dir(self):

        download_dir = os.path.join(self.current, ".downloads")

        if os.path.exists(download_dir) == False: os.mkdir(download_dir)

        return download_dir

    def check_ffmpeg_extensions(self):

        ffmpeg_extensions = os.path.join(self.current, ".ffmpeg_extensions.txt")

        if os.path.exists(ffmpeg_extensions) == False:

            file = requests.get("https://raw.githubusercontent.com/pietrop/ffmpeg_formats_list/master/ffmpeg_extentions.js")

            open(".ffmpeg_extensions.txt", "w").write(file.content)
        
        return ffmpeg_extensions

class files():

    def __init__(self, download_dir, op_system):

        self.download_dir = download_dir
        self.op_system = op_system

    def extract(self, file_name = str):

        if os.path.isfile(file_name):

            relatives = file_name.split("/")
            parents = relatives[:len(relatives) - 2].join()
            file, suffix = relatives[len(relatives) - 1].split(".")

            return parents, file, suffix

        else: return file_name

    def copy(self, abs_path):

        match self.op_system:

            case "nt": comm = "copy"

            case _: comm = "cp"

        if os.path.isdir(abs_path):

            dirs = os.listdir(abs_path)

            os.system(f"{comm} {abs_path}")
    
    def convert(self, file_name):

        if os.path.isabs(file_name): 
            
            if os.path.isfile(file_name):
                
                parents, file, suffix= self.extract(file_name)
                song = pd.AudioSegment.from_file(f"{parents}/{file}.{suffix}", suffix)

            else:
                
                raise ("An error occurred while converting, no file was found")

        else:
            
            file, suffix = file_name.split(".")

            song = pd.AudioSegment.from_file(f"{self.download_dir}/{file}.{suffix}", suffix)

        song.export(f"{self.download_dir}/{file}.wav", "wav")

    def remove(self, file_name):

        os.remove(f"{self.download_dir}/{file_name}")

class downloader():

    def __init__(self, url, download_dir, op_system):

        self.url = url
        self.download_dir = download_dir
        self.op_system = op_system

    def download_stream(self):

        video = yt(self.url)
        stream = video.streams.get_audio_only("mp4")

        stream.download(output_path=self.download_dir)

        stream_filename = f"{video.title}.{stream.subtype}"

        file_handler = files(self.download_dir, self.op_system)
        
        file_handler.convert(stream_filename)

        file_handler.remove(stream_filename)

        self.output(stream_filename)

    def output(self, stream_filename=str):
        
        print(f"{stream_filename} was downloaded")
        
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
        data, fr = sf.read(f"{self.download_dir}/{song}")

        sd.play(data, fr)

        sd.wait()

class app():

    def __init__(self):

        directories = started()

        self.current = directories.current
        self.download_dir = directories.download_dir
        self.op_system = directories.op_system

    def exec(self):

        option = int(input("1. Play music downloaded\n"\
                        "2. Download music from YouTube\n"\
                        "3. Add music on local files\n"\
                        "\nOption: "))

        self.clear_screen()
        
        match option:

            case 1:

                sound = player(self.download_dir)
                song = sound.songs_listed()

                sound.play(song)

                self.clear_screen()

                self.exec()

            case 2:

                url = input("URL: ")
                downloads = downloader(url, self.download_dir, self.op_system)

                downloads.download_stream()

                self.clear_screen(True)

            case 3:

                abs_path = input("Introduce the absolute path of directory or file:")

                assert os.path.exists(abs_path) and os.path.isabs(abs_path)

                match abs_path:

                    case os.path.isfile(abs_path):

                        os.system()

            case _:

                print("Fill only with the proposed input")

                self.clear_screen(True)
                
                self.exec()

    def clear_screen(self, wait = False):

        if wait == True: os.system("pause")

        match self.op_system:

            case "nt":

                os.system("cls")

            case _:

                os.system("clear")

app().exec()
