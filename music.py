from __future__ import unicode_literals

import discord
import youtube_dl
import spotipy
import youtubesearchpython
from pytube import YouTube
from discord_slash import SlashContext
import urllib.request
import json, os

active_voices = {}

client_id = '1ec592e3af2347468523ab3177805dab'
secret = 'e7ec7f08ef714c51b057b0cb37400f39'

auth_manager = spotipy.SpotifyClientCredentials(client_id=client_id, client_secret=secret)
spotify = spotipy.Spotify(auth_manager=auth_manager)


#


async def get_from_spotify(result):
    performers = ""
    music = result['name']
    for names in result["artists"]:
        performers = performers + names["name"] + ", "
    performers = performers.rstrip(", ")
    video = search(music, performers)
    name = f"{performers} - {music}"
    return [download_from_youtube(video), name]


def search(music, performers):
    videosSearch = youtubesearchpython.VideosSearch(f'{performers} - {music}', limit=1)
    videoresult = videosSearch.result()["result"][0]["link"]
    return videoresult


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192'
    }],
    'postprocessor_args': [
        '-ar', '32000'
    ],
    'prefer_ffmpeg': True,
    'keepvideo': True
}


def download_from_youtube(url):
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()

    out_file = video.download(output_path=os.path.join(os.getcwd(), 'music'))

    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    if not os.path.exists(new_file):
        os.rename(out_file, new_file)
    return new_file


#


class Music:
    
    def __init__(self,
                 client: discord.Client,
                 voice_channel: discord.VoiceChannel):
        self.client = client
        self.voice_channel = voice_channel
        self.queue = []
        self.now = ''
        
        active_voices[self.voice_channel] = self
    
    async def connect(self):
        try:
            await self.voice_channel.guild.voice_client.disconnect()
        except discord.errors.ClientException:
            pass
        except AttributeError:
            pass
        await self.voice_channel.connect()
        print(active_voices)
    
    async def play(self, ctx: SlashContext, music: str):
        
        await ctx.defer()
        
        if music.startswith('https://open.spotify.com/track/'):
            result = spotify.track(music)
            music = result['name']
            performers = ''
            for names in result["artists"]:
                performers = performers + names["name"] + ", "
            performers = performers.rstrip(", ")
            name = f'{performers} - {music}'
            filename = (await get_from_spotify(result))[0]
        elif music.startswith('https://www.youtube.com/watch?v='):
            filename = download_from_youtube(music)
            name = json.loads(urllib.request.urlopen(music))['entry']['title']['$t']
        else:
            videosSearch = youtubesearchpython.VideosSearch(music, limit=1)
            videoresult = videosSearch.result()["result"][0]["link"]
            filename = download_from_youtube(videoresult)
            name = videosSearch.result()["result"][0]["title"]
            print(videosSearch.result()["result"][0])
        
        print(filename)
        
        audio_source = discord.FFmpegPCMAudio(source=filename, executable='ffmpeg.txt')
        
        voice_client: discord.VoiceClient = ctx.guild.voice_client
        
        voice_client.play(audio_source)

        await ctx.reply(f'сейчас играет: {name}')

        # if len(self.queue) > 0:
        #     self.queue.append()
    
    async def delete(self):
        await self.voice_channel.guild.voice_client.disconnect()
        del active_voices[self.voice_channel]
        del self
