import base64
from urllib.parse import unquote
from .data_structures import AlbumItem, SongItem

def get_decoded_image_file(path_to_image):
    encoded_image = base64.b64encode(open(path_to_image, "rb").read())
    return "data:image/png;base64,{}".format(encoded_image.decode())


class CardItem:
    def __init__(self, name, info, image):
        self.title = name
        self.subtitle = info
        self.img_src = image


def make_now_playing_card(song: SongItem):
    content = CardItem(song.title, song.artist, get_decoded_image_file(song.artwork_path))
    return content


def make_artist_cards(artists):
    artist_content = []
    for result in artists.find({}).collation({'locale': 'en'}).sort('artistName', 1):
        artist_name = result['artistName']
        artist_profile_pic = result['profilePicLoc']
        artist_content.append(
            CardItem(artist_name, None, get_decoded_image_file(artist_profile_pic))
        )
    return artist_content


def make_album_cards(albums):
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


def make_album_content(albums, songs, album_name):
    album_name_parsed = unquote(album_name)
    result = albums.find_one({'albumName': album_name_parsed})
    songs_dict = {}
    for song_id in result['songs']:
        song = songs.find_one({"_id": song_id})
        songs_dict[int(song['trackNumber'])] = SongItem(song)
    songs_sorted = [songs_dict[k] for k in sorted(songs_dict.keys())]
    return AlbumItem(
        result['albumName'],
        result['albumArtist'],
        get_decoded_image_file(result['albumArtworkLoc']),
        songs_sorted)


def make_artist_view_cards(artists, albums, artist_name):
    artist_name_parsed = unquote(artist_name)
    result = artists.find_one({'artistName': artist_name_parsed})
    artist_content = []
    for album_id in result['artistAlbums']:
        album = albums.find_one({'_id': album_id})
        artist_content.append(
            CardItem(
                album['albumName'],
                None,
                get_decoded_image_file(album['albumArtworkLoc'])
            )
        )
    return artist_content


def make_songs_table(songs):
    results = songs.find({}).collation({'locale': 'en'}).sort('artistName', 1)
    return [SongItem(song) for song in results]


def make_playlist_cards(playlists):
    results = playlists.find({}).sort('playlistName', 1)
    return None#[PlaylistItem(playlist) for playlist in results]