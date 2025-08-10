import sys
import logging
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from flask import Flask, url_for, render_template, redirect, request, jsonify
from helper.muse_player import MusePlayer
from helper.content_generator import make_artist_cards, make_album_cards,  make_album_content, \
   make_artist_view_cards, make_songs_table, make_now_playing_card, get_decoded_image_file
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)


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
    logger.setLevel(logging.WARNING)

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
    # Not yet implemented
    return redirect("/artists")


@app.route("/playlists")
def show_all_playlists():
    # Not yet implemented
    return redirect("/artists")
    

@app.route("/playlists/<query_param>")
def show_playlist_page():
    # Not yet implemented
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


@app.route("/nowplaying")
def now_playing():
    current_song = muse_player.get_now_playing()

    return render_template(
        'now-playing-view.html',
        now_playing=current_song,
        player_content=make_now_playing_card(current_song),
        song_link_dest=url_for('show_album_view', query_param=current_song.album),
        artist_link_dest=url_for('show_artists_page', query_param=current_song.album_artist),
        repeat_mode=muse_player.get_repeat_mode(),
        is_playing=muse_player.is_playing(),
        shuffle_mode=muse_player.get_shuffle_mode()
    )

@app.route("/nowplaying/json")
def now_playing_json():
    current_song = muse_player.get_now_playing()
    elapsed_time_formatted = muse_player.get_elapsed_and_remaining_time()["elapsed_time"]
    remaining_time_formatted = muse_player.get_elapsed_and_remaining_time()["remaining_time"]   

    repeat_mode_labels = {0: "repeat_none", 1: "repeat_all", 2: "repeat_one"}
    repeat_mode = repeat_mode_labels[muse_player.get_repeat_mode()]

    shuffle_mode_labels = {0: "shuffle_off", 1: "shuffle_on"}
    shuffle_mode = shuffle_mode_labels[muse_player.get_shuffle_mode()]

    return jsonify({
        "title": current_song.title,
        "artist": current_song.artist,
        "album_art": get_decoded_image_file(current_song.artwork_path),
        "elapsed": elapsed_time_formatted,
        "remaining": remaining_time_formatted,
        "is_playing": muse_player.is_playing(),
        "shuffle_mode": shuffle_mode,
        "repeat_mode": repeat_mode,
    })


# @app.route("/changesong", methods=['POST'])
# def change_song():
#     if request.method == "POST":
#         muse_player.autoplay_next()
#     return jsonify({"status": "success"})


@app.route("/play", methods=['POST'])
def bg_play():
    is_playing = muse_player.play_or_pause()
    print ({"status": "success", "is_playing": is_playing})
    return jsonify({"status": "success", "is_playing": is_playing})


@app.route("/timer", methods=['POST', 'GET'])
def bg_time_progress():
    song_info_dict = muse_player.get_player_info()
   # pp.pprint(song_info_dict)  # For debugging purposes
    return jsonify(song_info_dict)


@app.route("/rewind", methods=['POST'])
def bg_rewind():
    if request.method == "POST":
        muse_player.seek_backward()
    return jsonify({"status": "success"})


@app.route("/fast-forward", methods=['POST'])
def bg_fastforward():
    if request.method == "POST":
        muse_player.seek_forward()
    return jsonify({"status": "success"})


@app.route("/shuffle", methods=['POST'])
def toggle_shuffle():
    new_mode = muse_player.toggle_shuffle_mode()
    shuffle_mode_labels = {0: "shuffle_off", 1: "shuffle_on"}
    pp.pprint({"status": "success", "new_mode": shuffle_mode_labels[new_mode]})
    return jsonify({"status": "success", "new_mode": shuffle_mode_labels[new_mode]})


@app.route("/change-repeat", methods=['POST'])
def bg_alter_repeat_mode():
    new_mode = muse_player.toggle_repeat_mode()
    repeat_mode_labels = {0: "repeat_none", 1: "repeat_all", 2: "repeat_one"}
    pp.pprint({"status": "success", "new_mode": repeat_mode_labels[new_mode]})
    return jsonify({"status": "success", "new_mode": repeat_mode_labels[new_mode]})


if __name__ == "__main__":
    app.run(debug=True)
