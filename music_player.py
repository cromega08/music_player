from ast import match_case
from genericpath import isdir, isfile
from time import sleep
from pytube import YouTube as yt
import sounddevice as sd
import soundfile as sf
import pydub as pd
import requests
import os
import re

class started():

    def __init__(self):
        
        self.current = os.getcwd()
        self.download_dir = self.check_download_dir()
        self.ffmpeg_extensions = self.check_ffmpeg_extensions()
        self.op_system = os.name

    def check_download_dir(self):

        download_dir = os.path.join(self.current, ".downloads")

        if os.path.exists(download_dir) == False: os.mkdir(download_dir)

        return download_dir

    def check_ffmpeg_extensions(self):

        ffmpeg_extensions = os.path.join(self.current, ".ffmpeg_extensions.txt")

        if os.path.exists(ffmpeg_extensions) == False:

            file = requests.get("https://raw.githubusercontent.com/pietrop/ffmpeg_formats_list/master/ffmpeg_extentions.js", allow_redirects=True)

            with open(".ffmpeg_extensions.txt", "w") as extensions:
                
                refined_text = str(file.content).replace("module.exports= ", "")
                extensions.write(refined_text)
        
        return ffmpeg_extensions

class files():

    def __init__(self, download_dir, op_system):

        self.download_dir = download_dir
        self.op_system = op_system

    def extract(self, file_name = str):

        if os.path.isfile(file_name):

            relatives = file_name.split("/")
            parents = "/".join(relatives[:len(relatives) - 2])
            file, suffix = relatives[len(relatives) - 1].split(".")

            return parents, file, suffix

        else: return file_name

    def copy(self, abs_path, ffmpeg_extensions):

        match self.op_system:

            case "nt": comm = "copy"

            case _: comm = "cp"

        if os.path.isfile(abs_path): 
            
            parents, file, suffix = self.extract(abs_path)

            if suffix in open(ffmpeg_extensions, "r").read():

                new_location = os.path.join(self.download_dir, f"{file}.{suffix}")

                print(new_location)
                
                os.system(f"{comm} {abs_path} {new_location}")

                self.convert(new_location)

                self.remove(new_location)
            
            else:

                raise ("An error occurred while converting, no audio file was found")

        else:

            dir_origin = os.listdir(abs_path)

            for music_files in dir_origin:

                old_location = os.path.join(abs_path, music_files)
                new_location = os.path.join(self.download_dir, music_files)

                os.system(f"{comm} {old_location} {new_location}")

                self.convert(new_location)

                self.remove(new_location)
        
        print("Transfer completed")
    
    def convert(self, file_name):

        if os.path.isabs(file_name): 

            print(os.path.isfile(file_name))
            
            if os.path.isfile(file_name):
                
                parents, file, suffix= self.extract(file_name)
                song = pd.AudioSegment.from_file(f"{parents}/{file}.{suffix}", suffix)

            else:
                
                raise ("An error occurred while converting, no file was found")

        else:

            relatives = file_name.split(".")
            
            file, suffix = "".join(relatives[:len(relatives)-1]), relatives[len(relatives)-1]
            
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

        stream_filename = f"{video.title}.{stream.subtype}"

        stream.download(output_path=self.download_dir)

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
        
        data, sr = sf.read(f"{self.download_dir}/{song}")
        
        sd.play(data, sr)

        sd.wait()

class app():

    def __init__(self):

        directories = started()

        self.current = directories.current
        self.download_dir = directories.download_dir
        self.ffmpeg_extensions = directories.ffmpeg_extensions
        self.op_system = directories.op_system

    def exec(self):

        option = int(input("1. Play music downloaded\n"\
                            "2. Download music from YouTube\n"\
                            "3. Add music on local files\n"\
                            "\nOption: "))

        self.clear_screen(True)
            
        match option:

            case 1:

                music = player(self.download_dir)
                song = music.songs_listed()

                music.play(song)

                self.clear_screen()

                self.exec()

            case 2:

                url = input("URL: ")

                assert any([domains in url for domains in ["youtube", "youtu.be"]])

                downloader(url, self.download_dir, self.op_system).download_stream()

                self.clear_screen(True)
            
            case 3:

                abs_path = input("Introduce the abs_path of the file: ")

                assert os.path.isabs(abs_path) and os.path.exists(abs_path)

                files(self.download_dir, self.op_system).copy(abs_path, self.ffmpeg_extensions)

                self.clear_screen(True)

            case _:

                print("Fill only with the proposed input")

                self.clear_screen(True)
                    
                self.exec()

    def clear_screen(self, wait = False):

        match self.op_system:

            case "nt":

                if wait == True: os.system("pause")

                os.system("cls")

            case "posix":

                if wait == True: os.system("read -n 1 -s -p 'Pulse any key to continue...'")

                os.system("clear")

app().exec()

