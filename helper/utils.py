from collections import namedtuple
import math
from urllib.parse import unquote
import base64
import dash_bootstrap_components as dbc
import dash_html_components as html
from pymongo import MongoClient

class CardItem:
    def __init__(self, name, info, image):
        self.title = name
        self.subtitle = info
        self.img_src = image

class SongItem:
    def __init__(self, song_id, track_name, artist, album, track_number, duration, num_plays, is_favorited):
        self.song_id = song_id
        self.title = track_name
        self.artist = artist
        self.album = album
        self.track_number = track_number
        self.duration = duration
        self.num_plays = num_plays
        self.is_favorited = is_favorited

class AlbumItem:
    def __init__(self, title, artist, album_cover_art, songs):
        self.title = title
        self.artist = artist
        self.cover_art = album_cover_art
        self.songs = songs


NUM_COLS = 5

connection = MongoClient("mongodb://127.0.0.1:27017/museplayer")
db = connection.museplayer
albums = db.albums
artists = db.artists
songs = db.songs

def get_decoded_image_file(path_to_image):
    encoded_image = base64.b64encode(open(path_to_image, "rb").read())
    return "data:image/png;base64,{}".format(encoded_image.decode())

def make_artist_cards():
    artist_content = []
    for result in artists.find({}).collation({'locale': 'en'}).sort('artistName', 1):
        artist_name = result['artistName']
        artist_profile_pic = result['profilePicLoc']
        artist_content.append(
            CardItem(artist_name, None, get_decoded_image_file(artist_profile_pic))
        )
    return artist_content


def make_album_cards():
    album_content = []
    results = albums.find({}).collation({'locale': 'en'}).sort('albumArtist', 1)
    for result in results:
        album_name = result['albumName']
        artist_name = result['albumArtist']
        album_cover_art = result['albumArtworkLoc']
        album_content.append(
            CardItem(album_name, artist_name, get_decoded_image_file(album_cover_art))
        )
    return album_content


def make_album_content(album_name):
    album_name_parsed = unquote(album_name)
    result = albums.find_one({'albumName': album_name_parsed})
    songs = {}
    for song in result['songs']:
        duration = song['duration']
        minutes = int(duration//60)
        seconds = int((duration/60 - minutes)*60)
        if seconds < 10:
            seconds = str(0) + str(seconds)
        duration_fmt = f"{minutes}:{seconds}"
        song_item = SongItem(
            song['_id'], song['title'], song['artistName'], song['albumName'], 
            song['trackNumber'], duration_fmt, song['numPlays'], song['isFavorited']
        )
        songs[int(song['trackNumber'])] = song_item
    songs_sorted = [songs[k] for k in sorted(songs.keys())]
    return AlbumItem(result['albumName'], result['albumArtist'], get_decoded_image_file(result['albumArtworkLoc']), songs_sorted)


def make_artist_view_cards(artist_name):
    artist_name_parsed = unquote(artist_name)
    result = artists.find_one({'artistName': artist_name_parsed})
    artist_content = []
    for album_id in result['artistAlbums']:
        album = albums.find_one({'_id': album_id})
        artist_content.append(
            CardItem(album['albumName'], None, get_decoded_image_file(album['albumArtworkLoc']))
        )
    return artist_content

def make_songs_table():
    results = songs.find({}).collation({'locale': 'en'}).sort('artistName', 1)
    all_songs = []
    for song in results:
        duration = song['duration']
        minutes = int(duration//60)
        seconds = int((duration/60 - minutes)*60)
        if seconds < 10:
            seconds = str(0) + str(seconds)
        duration_fmt = f"{minutes}:{seconds}"
        all_songs.append(
            SongItem(
                song['_id'], song['title'], song['artistName'], song['albumName'], 
                song['trackNumber'], duration_fmt, song['numPlays'], song['isFavorited']
            )
        )
    return all_songs

def make_controls():
    pass