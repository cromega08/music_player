#GPL-3.0-or-later

from ast import match_case
from genericpath import isdir, isfile
from pytube import YouTube as yt, Playlist as pl
import sounddevice as sd
import soundfile as sf
import pydub as pd
import requests
import shutil as sh
from send2trash import send2trash as s2t
import os

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
            parents = "/".join(relatives[:len(relatives) - 1])
            file, suffix = relatives[len(relatives) - 1].split(".")

            print(parents, file, suffix)

            return parents, file, suffix

        else: return file_name

    def copy(self, abs_path, ffmpeg_extensions):

        if os.path.isfile(abs_path): 
            
            parents, file, suffix = self.extract(abs_path)

            if suffix in open(ffmpeg_extensions, "r").read():

                new_location = os.path.join(self.download_dir, f"{file}.{suffix}")

                sh.copy(abs_path, new_location)

                self.convert(new_location)

                self.remove(new_location)
            
            else: raise Exception("An error occurred while converting, no audio file was found")

        else:

            dir_origin = os.listdir(abs_path)

            for music_files in dir_origin:

                old_location = os.path.join(abs_path, music_files)
                new_location = os.path.join(self.download_dir, music_files)

                sh.copy(old_location, new_location)

                self.convert(new_location)

                self.remove(new_location)
        
        print("Transfer completed")
    
    def convert(self, file_name):

        if os.path.isabs(file_name): 

            parents, file, suffix= self.extract(file_name)

            if os.path.isfile(file_name): song = pd.AudioSegment.from_file(file_name, suffix)

            else: raise Exception("An error occurred while converting, no file was found")

        else:

            relatives = file_name.split(".")
            
            file, suffix = "".join(relatives[:len(relatives)-1]), relatives[len(relatives)-1]
      
            song = pd.AudioSegment.from_file(f"{self.download_dir}/{file_name}", suffix)

        song.export(f"{self.download_dir}/{file}.wav", "wav")

    def remove(self, file_name):

        if self.download_dir in file_name: s2t(file_name)
        
        else: s2t(os.path.join(self.download_dir, file_name))

class downloader():

    def __init__(self, download_dir, op_system):

        self.download_dir = download_dir
        self.op_system = op_system
        self.file_handler = files(self.download_dir, self.op_system)

    def download_audio(self, url, name = str):

        audio = yt(url)
        stream = audio.streams.get_audio_only("mp4")
        stream_filename = f"{audio.title}.{stream.subtype}" if name == "non" else f"{name}.{stream.subtype}"

        stream.download(output_path = self.download_dir, filename = stream_filename)
        
        self.file_handler.convert(stream_filename)

        self.file_handler.remove(stream_filename)

        print(f"{stream_filename} was downloaded")

    def download_playlist(self, url):

        playlist = pl(url)

        for video in playlist.videos:

            stream = video.streams.get_audio_only("mp4")
            stream_filename = f"{video.title}.{stream.subtype}"

            stream.download(output_path = self.download_dir, filename = stream_filename)

            self.file_handler.convert(stream_filename)

            self.file_handler.remove(stream_filename)

        print(f"{playlist.title} was downloaded")
    
    def print_playlist(self, url):

        playlist = pl(url)
        count = 0

        for video in playlist.videos: count += 1, print(f"{count}. -Stream: {video.title}\n{len(str(count)) + 1} -URL: {playlist.video_urls[count-1]}")

    def print_audio_data(self, url):

        audio = yt(url)
        stream = audio.streams.get_audio_only("mp4")

        print(f"""Name: {audio.title}\n
        Author: {audio.author}\n
        Length: {audio.length}\n
        Size: {stream.filesize}\n
        Views and rating: {audio.views} | {audio.rating}\n
        Date: {audio.publish_date}""")

class player():

    def __init__(self, download_dir):
        
        self.download_dir = download_dir
        self.music = os.listdir(self.download_dir)

    def songs_listed(self):

        for songs in self.music: print(f"{self.music.index(songs)+1}. {songs}".replace("_", " "))

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

        self.clear_screen()
            
        match option:

            case 1:

                music = player(self.download_dir)
                song = music.songs_listed()

                music.play(song)

                self.clear_screen()

                self.exec()

            case 2:

                option = int(input("1. Download a video\n"\
                                "2. Download a playlist\n"\
                                "\nOption: "))

                self.clear_screen()

                download = downloader(self.download_dir, self.op_system)

                match option:

                    case 1:

                        url = input("Video URL: ")

                        assert any([domains in url for domains in ["youtube", "youtu.be"]]) and "watch" in url

                        download.print_audio_data(url)

                        aprobe = input("Confirm the download? (y/n): ")

                        match aprobe:

                            case "y" | "yes":

                                change = input("Want to rename the file? (y/n): ")

                                match change:

                                    case "y" | "yes": new_name = input("New name (without suffix [ex. '.mp4']): ")
                                    
                                    case "n" | "no": new_name = "non"

                                download.download_audio(url, new_name)

                                self.clear_screen(True)

                                self.exec()

                            case "n" | "no":

                                print("Canceling download")

                                self.clear_screen(True)

                                self.exec()
                            
                            case _:

                                print("Invalid input")

                                self.clear_screen(True)

                                self.exec()
                    
                    case 2:
                        
                        url = input("Playlist url")

                        assert any([domains in url for domains in ["youtube", "youtu.be"]]) and "playlist" in url

                        download.print_playlist(url)

                        aprobe = input("Confirm the download? (y/n): ")

                        match aprobe:

                            case "y" | "yes":

                                download.download_playlist(url)
                                
                                self.clear_screen(True)
                                
                                self.exec()

                            case "n" | "no":

                                print("Canceling download")

                                self.clear_screen(True)

                                self.exec()
                            
                            case _:

                                print("Invalid input")

                                self.clear_screen(True)

                                self.exec()
                        
                    case _:

                        print("Invalid input")

                        self.clear_screen(True)

                        self.exec()
            
            case 3:

                abs_path = input("Introduce the abs_path of the file: ")

                assert os.path.isabs(abs_path) and os.path.exists(abs_path)

                files(self.download_dir, self.op_system).copy(abs_path, self.ffmpeg_extensions)

                self.clear_screen(True)

                self.exec()

            case _:

                print("Invalid input")

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