import os
import json
from datetime import date
from flask import Flask, url_for, render_template, send_from_directory, request, redirect
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from bson.objectid import ObjectId
from helper.utils import make_artist_cards, make_album_cards,  make_album_content, \
   make_artist_view_cards, make_songs_table

app = Flask(__name__)
Bootstrap(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/museplayer"
mongo = PyMongo(app)
db = mongo.db

@app.route("/")
def show_homepage():
    return redirect("/artists")

@app.route("/playlists")
def show_playlists():
    return redirect("/artists")

@app.route("/artists")
def show_all_artists():
    artist_content = make_artist_cards()
    return render_template(
        'card-grid-view.html',
        page_url=url_for('show_all_artists'),
        img_dest='show_artists_page',
        page_title="Artists",
        content=artist_content
        )


@app.route("/artists/<query_param>")
def show_artists_page(query_param):
    artist_view = make_artist_view_cards(query_param)
    return render_template(
        'card-grid-view.html', 
        page_url=url_for('show_artists_page', query_param=query_param),
        img_dest='show_album_view',
        page_title=query_param,
        content=artist_view
        )


@app.route("/albums")
def show_all_albums():
    album_content = make_album_cards()
    return render_template(
        'card-grid-view.html',
        page_url=url_for('show_all_albums'),
        img_dest='show_album_view',
        page_title="Albums",
        content=album_content
        )


@app.route("/albums/<query_param>")
def show_album_view(query_param):
    page_content = make_album_content(query_param)
    return render_template(
        'album-view.html',
        page_url=url_for('show_album_view', query_param=query_param),
        page_title=query_param,
        album=page_content
        )


@app.route("/songs")
def show_all_songs():
    song_content = make_songs_table()
    return render_template(
        'song-view.html',
        page_url=url_for('show_all_songs'),
        page_title="Songs",
        content=song_content
        )

if __name__ == "__main__":
    app.run(debug=True)