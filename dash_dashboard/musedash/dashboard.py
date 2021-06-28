"""Instantiate a Dash app."""
import os
from .utils import * 
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from muse_player import MusePlayer

def init_muse_dashboard(server):
    """Create a Muse Player dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix="/",
        external_stylesheets=['./assets/css/cyborg.css', './assets/css/custom-styling.css'],
        suppress_callback_exceptions=True,
        update_title=None
    )

    dash_app.title = "Muse Player"

    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
    }

    CONTENT_STYLE = {
        "margin-left": "2rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",
    }

    ICONS_DIR = './assets/icons/controls/'
    MUSIC_DIR = os.environ.get("MUSIC_DIR")
    sidebar = dbc.Container(
        [
            html.H2("Muse", className="display-4"),
            html.Hr(),
            html.P(
                " A Music Player written in Python", className="lead"
            ),
            html.H3("Library", className="display-5"),
            html.Hr(),
            dbc.Nav(
                [
                    dbc.NavLink("Home", href="/", active="exact"),
                    dbc.NavLink("Playlists", href="/Playlists", active="exact"),
                    dbc.NavLink("Artists", href="/Artists", active="exact"),
                    dbc.NavLink("Albums", href="/Albums", active="exact"),
                    dbc.NavLink("Songs", href="/Songs", active="exact"),
                    dbc.NavLink("Now Playing", href="/NowPlaying", active="exact")
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style=SIDEBAR_STYLE,
        fluid=False
    )

    album_cards = make_album_cards(MUSIC_DIR)

    album_deck = make_display_table(cards=album_cards, num_columns=5)

    album_view = dbc.Container(
        children=[
            html.H4('Albums', className='aligned-page-title'),

            html.Hr(),
            dbc.Table([html.Tbody(album_deck)])
        ],
        fluid=False
    )

    artist_cards = make_artist_cards(MUSIC_DIR)

    artist_deck = make_display_table(cards=artist_cards, num_columns=5)

    artist_view = dbc.Container(
        children=[
            html.H4('Artists', className='aligned-page-title'),
            html.Hr(),
            dbc.Table([html.Tbody(artist_deck)], style={'border': 'none'})
        ],
        fluid=False
    )

    song_view = dbc.Card(
        [
            html.Img(src=get_decoded_image_file(MUSIC_DIR + '/Flora Cash/Missing Home (filous remix)/AlbumArtwork.jpeg'), height='500px', width='500px'),
            html.B(
                children=[
                    'Missing Home (filous remix)'
                ]
            ),
            html.A(
                children=[
                    'Flora Cash'
                ], href='/Artists/Flora Cash'
            ),
            make_controls()
        ],
        body=True, 
        style={'width': '540px', 'border': 'none'}
    )

    now_playing_view = dbc.Container(
        [
            html.H4('Now Playing', className='aligned-page-title'),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(song_view)
                ],
                no_gutters=False
            )
        ],
        fluid=False
    )

    generic_unfinished_view = dbc.Container(
        [
            html.H4("This page has not been finished yet!", className='aligned-page-title'),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(html.B("Good things to come!"))
                ],
                no_gutters=False
            )
        ],
        fluid=False
    )

    content = html.Div(id="page-content", style=CONTENT_STYLE)

    dash_app.layout = html.Div(
        [
            dcc.Location(id="url"), 
            sidebar, 
            content
        ]
    )

    error_404_view = dbc.Container(
        [
            html.H4("You've reached a page that doesn't exist!", className='aligned-page-title'),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(html.A("Please click here to return to the homepage", href="/"))
                ],
                no_gutters=False
            )
        ],
        fluid=False
    )

    @dash_app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page_content(pathname):
        if pathname == "/":
            return generic_unfinished_view
        elif pathname == "/Playlists":
            return generic_unfinished_view
        elif pathname == "/Artists":
            return artist_view
        elif pathname == "/Albums":
            return album_view
        elif pathname == "/Songs":
            return generic_unfinished_view
        elif pathname == "/NowPlaying":
            return now_playing_view
        return error_404_view

    filepath = MUSIC_DIR + '/Flora Cash/Missing Home (filous remix)/01 Missing Home (filous remix).m4a'
    MP = MusePlayer(filepath, repeat_type=1)

    @dash_app.callback(
        Output("play-pause", "children"),
        [Input("play-pause", "n_clicks")])
    def play_or_pause(n_clicks):
        if not n_clicks: # No clicks yet i.e. autoplaying (OPTION when autoplaying should be to PAUSE)
            MP.play()
            icon_to_show = html.Img(src=ICONS_DIR + 'pause.png')
            print('no clicks yet')
        if n_clicks:
            if n_clicks % 2 == 1:  # 1 clicks i.e. paused (OPTION when paused should be to PLAY)
                print(n_clicks)
                MP.pause()
                icon_to_show = html.Img(src=ICONS_DIR + 'play.png')
            else:  # 2 clicks i.e. playing (OPTION when playing should be to PAUSE)
                MP.play()
                icon_to_show = html.Img(src=ICONS_DIR + 'pause.png')
                print(n_clicks)
        return icon_to_show

    @dash_app.callback(
        Output("rewind", "children"),
        [Input("rewind", "n_clicks")])
    def rewind(n_clicks):
        if n_clicks:
            MP.seek_backward(n_clicks)
            return html.Img(src=ICONS_DIR + 'rewind.png')
        else:
            raise dash.exceptions.PreventUpdate

    @dash_app.callback(
        Output("fast-forward", "children"),
        [Input("fast-forward", "n_clicks")])
    def fforward(n_clicks):
        if n_clicks:
            MP.seek_forward(n_clicks)
            return html.Img(src=ICONS_DIR + 'fast-forward.png')
        else:
            raise dash.exceptions.PreventUpdate



    @dash_app.callback(
        Output("repeat", "children"),
        [Input("repeat", "n_clicks")])
    def repeat_type(n_clicks):
        if n_clicks:
            if n_clicks % 3 == 1:
                MP.set_next_repeat_type(-1)
                return html.Img(src=ICONS_DIR + 'repeat-all.png')
            elif n_clicks % 3 == 2:
                MP.set_next_repeat_type(1)
                return html.Img(src=ICONS_DIR + 'repeat-one-on.png')
            elif n_clicks % 3 == 0:
                MP.set_next_repeat_type(0)
                return html.Img(src=ICONS_DIR + 'repeat-off.png')
        else:
            MP.set_next_repeat_type(0)
            return html.Img(src=ICONS_DIR + 'repeat-off.png')


    @dash_app.callback(
        Output("shuffle", "children"),
        [Input("shuffle", "n_clicks")]
    )
    def shuffle_on_or_off(n_clicks):
        if n_clicks:
            if n_clicks % 2 == 1: # 0 clicks = off, 1 click = on, 2 clicks is off
                return html.Img(src=ICONS_DIR + 'shuffle-on.png')
            else:
                return html.Img(src=ICONS_DIR + 'shuffle-off.png')
        else:
            return html.Img(src=ICONS_DIR + 'shuffle-off.png')
    
    return dash_app.server

