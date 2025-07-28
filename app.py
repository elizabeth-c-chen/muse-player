import sys
import logging
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from flask import Flask, url_for, render_template, redirect, request
from helper.muse_player import MusePlayer
from helper.content_generator import make_artist_cards, make_album_cards,  make_album_content, \
   make_artist_view_cards, make_songs_table, make_now_playing_card



app = Flask(__name__)
Bootstrap(app)
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/museplayer"

mongo = PyMongo(app)
db = mongo.db

albums = db.albums
artists = db.artists
songs = db.songs

muse_player = MusePlayer()

def setup_logger(logger, output_file):
    logger.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter('%(asctime)s [%(funcName)s]: %(message)s'))
    logger.addHandler(stdout_handler)

    file_handler = logging.FileHandler(output_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(funcName)s] %(message)s'))
    logger.addHandler(file_handler)


logger = logging.Logger(__name__)
setup_logger(logger, 'debug_output.log')


@app.route("/")
def show_homepage():
    return redirect("/artists")


@app.route("/playlists")
def show_all_playlists():
    return redirect("/artists")
    

@app.route("/playlists/<query_param>")
def show_playlist_page():
    playlist_content =  None # TODO
    return redirect("/artists")
    # return render_template(
    #     'playlist-view.html',
    #     page_url=url_for('show_all_playlists'),
    #     iimg_dest='show_playlists_page',
    #     page_title='Playlists',
    #     content=playlist_content
    # )


@app.route("/artists")
def show_all_artists():
    artist_content = make_artist_cards(artists)
    return render_template(
        'card-grid-view.html',
        page_url=url_for('show_all_artists'),
        img_dest='show_artists_page',
        page_title="Artists",
        content=artist_content
        )


@app.route("/artists/<query_param>")
def show_artists_page(query_param):
    artist_view = make_artist_view_cards(artists, albums, query_param)
    return render_template(
        'card-grid-view.html',
        page_url=url_for('show_artists_page', query_param=query_param),
        img_dest='show_album_view',
        page_title=query_param,
        content=artist_view
        )


@app.route("/albums")
def show_all_albums():
    album_content = make_album_cards(albums)
    return render_template(
        'card-grid-view.html',
        page_url=url_for('show_all_albums'),
        img_dest='show_album_view',
        page_title="Albums",
        content=album_content
        )


@app.route("/albums/<query_param>")
def show_album_view(query_param):
    page_content = make_album_content(albums, songs, query_param)
    return render_template(
        'album-view.html',
        page_url=url_for('show_album_view', query_param=query_param),
        page_title=query_param,
        album=page_content
        )


@app.route("/songs")
def show_all_songs():
    song_content = make_songs_table(songs)
    return render_template(
        'song-view.html',
        page_url=url_for('show_all_songs'),
        page_title="Songs",
        content=song_content
        )


@app.route("/nowplaying", methods=['GET'])
def now_playing():
    if request.method == "GET":
        current_song = muse_player.get_now_playing()
        player_content = make_now_playing_card(current_song)
        print(logger.debug(current_song.title))
        return render_template(
            'now-playing-view.html',
            now_playing=current_song,
            player_content=make_now_playing_card(current_song),
            song_link_dest=url_for('show_album_view', query_param=current_song.album),
            artist_link_dest=url_for('show_artists_page', query_param=current_song.album_artist)
        )
        
@app.route("/changesong", methods=['POST'])
def change_song():
    if request.method == "POST":
        muse_player.autoplay_next()
    return "success"

@app.route("/play", methods=['POST'])
def bg_play():
    if request.method == "POST":
        muse_player.play_or_pause()
    return "success"


@app.route("/timer", methods=['POST', 'GET'])
def bg_time_progress():
    time_dict = muse_player.get_elapsed_and_remaining_time()
    #if time_dict["remainingSeconds"] <= 1:
    #    muse_player.autoplay_next()
    #print(logger.debug(time_dict))
    print(logger.debug(time_dict["songHasChanged"]))
    return time_dict


@app.route("/rewind", methods=['POST'])
def bg_rewind():
    if request.method == "POST":
        muse_player.seek_backward()
    return "success"


@app.route("/fast-forward", methods=['POST'])
def bg_fastforward():
    if request.method == "POST":
        muse_player.seek_forward()
    return "success"


# @app.route("/shuffle", methods=['POST'])
# def bg_shuffle():
#     if request.method == "POST":
#         pass
#        # muse_player.shuffle_queue()
#     return "success"


# @app.route("/change-repeat", methods=['POST'])
# def bg_alter_repeat_mode():
#     if request.method == "POST":
#         pass
#        # muse_player.set_next_repeat_type()
#     return "success"


if __name__ == "__main__":
    app.run(debug=True)
