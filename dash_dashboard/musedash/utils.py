import os
import math
import base64
import dash_bootstrap_components as dbc
import dash_html_components as html

def get_num_total_rows(cards, num_columns):
    return len(cards)//num_columns + 1

def get_decoded_image_file(path_to_image):
    encoded_image = base64.b64encode(open(path_to_image, "rb").read())
    return "data:image/png;base64,{}".format(encoded_image.decode())


def make_album_cards(music_dir):
    album_cards = []
    for artist_name in os.scandir(music_dir): 
        if artist_name.is_dir():
            path_to_artist = "{}/{}".format(music_dir, artist_name.name)
            artist_albums = os.scandir(path_to_artist)
            for album in artist_albums:
                if album.is_dir():
                    path_to_artwork = "{}/{}/AlbumArtwork.jpeg".format(path_to_artist, album.name)
                    card_content = [
                        html.A(children=[dbc.CardImg(src=get_decoded_image_file(path_to_artwork))], href="/Albums/{}".format(album.name)),
                        html.A(children=[html.B(album.name)], href="/Albums/{}".format(album.name), className='bold-info-text'),
                        html.A(children=[html.P(artist_name.name)], href="/Artists/{}".format(artist_name.name), className='regular-info-text')
                    ]
                    card = dbc.Card(card_content, style={'width': '16rem', 'padding': '5px'})
                    album_cards.append(card)
    return album_cards


def make_artist_cards(music_dir):
    artist_cards = []
    for artist_name in os.scandir(music_dir):
        if artist_name.is_dir():
            artist_profile_pic = "{}/{}/ProfilePic.jpeg".format(music_dir, artist_name.name)
            card_content = [
                        html.A(children=[dbc.CardImg(src=get_decoded_image_file(artist_profile_pic))], href="/Artists/{}".format(artist_name.name)),
                        html.A(children=[html.B(artist_name.name)], href="/Artists/{}".format(artist_name.name), className='bold-info-text')
                    ]
            card = dbc.Card(card_content, style={'width': '16rem', 'padding': '5px'})
            artist_cards.append(card)
    return artist_cards


def make_display_table(cards, num_columns):
    num_total_rows = get_num_total_rows(cards, num_columns)
    table_rows = [None] * num_total_rows
    row_counter = 0
    row_cells = [None] * num_columns
    cell_counter = 0
    for i in range(len(cards)):
        row_cells[cell_counter] = html.Td(cards[i])
        cell_counter += 1
        if cell_counter == num_columns:
            table_rows[row_counter] = html.Tr(row_cells)
            row_counter += 1
            cell_counter = 0
            row_cells = [None] * num_columns
        elif i == len(cards) - 1:
            table_rows[row_counter] = html.Tr(row_cells)
    return table_rows


def make_controls():
    UI_BUTTON_STYLE = {'width': '55px', 'padding': '2.5px', 'margin-left': '5px', 'margin-right': '5px', 'background': 'transparent', 'border': 'none'}
    ICONS_DIR = './assets/icons/controls/'
    controls = html.Div(
        [
            dbc.Button(
                children=[
                    html.Img(src=ICONS_DIR + 'shuffle.png')
                ],
                id='shuffle',
                style=UI_BUTTON_STYLE
            ),
            dbc.Button(
                children=[
                    html.Img(src=ICONS_DIR + 'rewind.png')
                ],
                id='rewind',
                style=UI_BUTTON_STYLE
            ),
            dbc.Button(
                children=[
                    html.Img(src=ICONS_DIR + 'pause.png')
                ],
                id='play-pause',
                style=UI_BUTTON_STYLE
            ),
            dbc.Button(
                children=[
                    html.Img(src=ICONS_DIR + 'fast-forward.png')
                ],
                id='fast-forward',
                style=UI_BUTTON_STYLE
            ),
            dbc.Button(
                children=[
                    html.Img(src=ICONS_DIR + 'repeat-all.png')
                ],
                id='repeat',
                style=UI_BUTTON_STYLE
            )
        ],
        style={'margin': 'auto'}
    )
    return controls