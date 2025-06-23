from flask import Flask, redirect, render_template, request
from datetime import datetime
import pandas as pd
import sqlite3
import json

import plotly.express as px
import plotly.io as pio

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.df = None # Define a global dataframe variable so it can be used by all routes
app.colour_palette = ['#A8D5BA', '#D1B3E0', '#F7C8C8', '#BFD7ED', '#FFE1A8', '#D9D9D9']

# Define aliases to save typing out long strings each time I want to access data
ALBUM = "master_metadata_album_album_name"
TRACK = "master_metadata_track_name"
ARTIST = "master_metadata_album_artist_name"

def clean_data(df):
    df = df[df['ms_played'] > 60000] # Filter for songs that were only listened to for > 1 minute
    df['ts'] = pd.to_datetime(df['ts'], utc=True)
    df
    #df['year'] = df['ts'].dt.year
    #df['month'] = df['ts'].dt.month
    #df['day'] = df['ts'].dt.day
    #df['hour'] = df['ts'].dt.hour
    df.drop(['spotify_track_uri', 'episode_name', 'offline_timestamp', 'incognito_mode', 'ip_addr', 'audiobook_title', 'audiobook_chapter_title', 'audiobook_uri', 'audiobook_chapter_uri', 'spotify_episode_uri', 'episode_show_name'], axis=1, inplace=True)
    return df

def create_plot_for_dash_main(col, year, index_str, colour_idx):
        if year != 0:
            df_filt = app.df.loc[(app.df['ts'].dt.year == year)]
        else:
            df_filt = app.df
        top = df_filt[col].value_counts().reset_index(name="count").head(10)
        top.rename(columns={'index':index_str}, inplace=True)
        fig = px.bar(top, x=index_str, y="count", title="")
        fig.update_layout(plot_bgcolor='white')
        fig.update_traces(marker_color=app.colour_palette[colour_idx])
        fig = pio.to_html(fig, full_html=False)
        return fig

def create_pie_for_dash_main(year):
    if year != 0:
        df_filt = app.df.loc[(app.df['ts'].dt.year == year)]
    else:
        df_filt = app.df
    top = df_filt[ARTIST].value_counts().reset_index(name="count")
    top.rename(columns={'index':'artist'}, inplace=True)
    top['artist'] = top['artist'].str.upper() # Convert artists to uppercase - for compatability with SQL db
    # ChatGPT assisted with reading sql queries into a dataframe, and merging with existing df
    with sqlite3.connect('fest.db') as con:
        genre_df = pd.read_sql('SELECT artist, genre FROM artists', con)
    merged_df = top.merge(genre_df, on='artist', how='left')

    genre_counts = merged_df['genre'].value_counts().reset_index() # Get value counts and convert back to df for plotly
    genre_counts.columns = ['genre', 'count']

    # Create pie chart, filter out any genres with a count < 1 so the number of slices is sensible
    fig = px.pie(genre_counts.loc[genre_counts['count'] > 1], names='genre', values='count', color_discrete_sequence=app.colour_palette)
    fig = pio.to_html(fig, full_html=False)
    return fig


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == 'POST':
        # ChatGPT assisted with reading in JSON files using a HTML form 
        # Flask documentation also assisted with the below code
        if 'file' not in request.files or request.files['file'].filename == '':
            # TODO: Implement a 400: Bad Request error page
            return "No file", 400
        else:
            file = request.files['file']
            data = file.read()
            app.df = pd.read_json(data)
            app.df = clean_data(app.df)
            return redirect("/dash_main")

@app.route("/dash_main", methods=['GET', 'POST'])
def dash_main():
    year = 0
    if request.method == 'POST':
        year = int(request.form.get("year"))

    # Check if user data has been uploaded, if not, redirect to the page to upload data
    if app.df is None:
        return redirect("/")
    else:
        year_array = app.df['ts'].dt.year.unique()
        # Bundled fig generation into a function as it was repetetive
        artist_fig = create_plot_for_dash_main(ARTIST, year, 'artist', 0)
        album_fig = create_plot_for_dash_main(ALBUM, year, 'album', 1)
        track_fig = create_plot_for_dash_main(TRACK, year, 'song', 2)
        genre_fig = create_pie_for_dash_main(year)

        return render_template('dash_main.html', years=year_array, artist_fig=artist_fig, album_fig=album_fig, track_fig=track_fig, genre_fig=genre_fig)

@app.route("/dash_artists", methods=['GET', 'POST'])
def dash_artists():
    # Check if the user has changed the number on the slider
    if request.method == 'POST':
        nrows = int(request.form.get("nrows"))
        start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
    else:
        nrows = 10

    # Check if user data has been uploaded, if not, redirect to the page to upload data
    if app.df is None:
        return redirect("/")
    else:  
        try:
            start_date
            artists_data = app.df.loc[(app.df['ts'].dt.date >= start_date) & (app.df['ts'].dt.date <= end_date)]
            artists_data = artists_data[ARTIST].value_counts()
        except NameError:          
            artists_data = app.df[ARTIST].value_counts()
        return render_template("dash_artists.html", data=artists_data, nrows=nrows)

@app.route("/dash_albums", methods=['GET', 'POST'])
def dash_albums():
    # Check if the user has changed the number on the slider
    if request.method == 'POST':
        nrows = int(request.form.get("nrows"))
        start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
    else:
        nrows = 10

    # Check if user data has been uploaded, if not, redirect to the page to upload data
    if app.df is None:
        return redirect("/")
    else:  
        try:
            start_date
            album_data = app.df.loc[(app.df['ts'].dt.date >= start_date) & (app.df['ts'].dt.date <= end_date)]
            # ChatGPT assisted with converting value_counts back to a dataframe and merging to get the associated artist
            album_data = album_data[ALBUM].value_counts().reset_index()
            album_data.columns = [ALBUM, 'Count']
            album_artist_data = album_data.merge(app.df[[ALBUM, ARTIST]].drop_duplicates(), on=ALBUM)
        except NameError:          
            album_data = app.df[ALBUM].value_counts().reset_index()
            album_data.columns = [ALBUM, 'Count']
            album_artist_data = album_data.merge(app.df[[ALBUM, ARTIST]].drop_duplicates(), on=ALBUM)
        return render_template("dash_albums.html", data=album_artist_data, nrows=nrows)

@app.route("/dash_songs", methods=['GET', 'POST'])
def dash_songs():
    # Check if the user has changed the number on the slider
    if request.method == 'POST':
        nrows = int(request.form.get("nrows"))
        start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
    else:
        nrows = 10

    # Check if user data has been uploaded, if not, redirect to the page to upload data
    if app.df is None:
        return redirect("/")
    else:  
        try:
            start_date
            song_data = app.df.loc[(app.df['ts'].dt.date >= start_date) & (app.df['ts'].dt.date <= end_date)]
            # ChatGPT assisted with converting value_counts back to a dataframe and merging to get the associated artist
            song_data = song_data[TRACK].value_counts().reset_index()
            song_data.columns = [TRACK, 'Count']
            song_artist_data = song_data.merge(app.df[[TRACK, ARTIST]].drop_duplicates(), on=TRACK)
        except NameError:          
            song_data = app.df[TRACK].value_counts().reset_index()
            song_data.columns = [TRACK, 'Count']
            song_artist_data = song_data.merge(app.df[[TRACK, ARTIST]].drop_duplicates(), on=TRACK)
        return render_template("dash_songs.html", data=song_artist_data, nrows=nrows)

@app.route("/festival_finder")
def festipal():
    if app.df is None:
        return redirect("/")
    else:  
        artists_data = app.df[ARTIST].value_counts().reset_index(name="count")
        artists_data.rename(columns={'index':'artist'}, inplace=True)
        artists_data.index += 1 # Start indexing from 1

    # Extract festival names
    with sqlite3.connect('fest.db') as con:
            cursor = con.cursor()
            festivals = cursor.execute('SELECT festival FROM festivals').fetchall()
    festivals = [row[0] for row in festivals]
    num_festivals = len(festivals)
    fest_scores = [0] * num_festivals

    # Fairly simple algorithm to determine best matched festivals
    for i in range(num_festivals):
        with sqlite3.connect('fest.db') as con:
            cursor = con.cursor()
            lineups = cursor.execute('SELECT l.artist_id, a.artist AS artist_name,\
                                    l.festival_id, f.festival AS festival_name,\
                                    l.headliner\
                                    FROM lineups2025 l\
                                    JOIN artists a ON l.artist_id = a.id\
                                    JOIN festivals f ON l.festival_id = f.id\
                                    WHERE f.id = ?;', (i+1, )).fetchall()
    
        count = 0
        for artist in lineups:
            if artist[4] == 1:
                weighting = 2 # Double weighting for headliners
            else:
                weighting = 1
            idx = artists_data[artists_data['artist'].str.upper() == artist[1]].index
            if idx.empty == False:
                idx = int(idx[0])
                weighting = weighting/(10+idx) # 10 fairly arbitrarily chosen so that top 1, 2, 3 etc artists weren't unreasonably heavily weighted
                count += weighting
            
        fest_scores[i] = count
    fest_data = dict(sorted(zip(festivals, fest_scores), key=lambda x: x[1], reverse=True))
    print(fest_data)
    top_3 = dict(list(fest_data.items())[:3]) # Filter to top 3 festivals

    # Get other details about the top 3 festivals, to populate the results cards and route to the festival page with the button
    festival_details = []
    for key in top_3.keys():
        with sqlite3.connect('fest.db') as con:
            cursor = con.cursor()
            festival_details.append(cursor.execute('SELECT * FROM festivals WHERE festival = ?', (key,)).fetchone())
    
    return render_template("festival_finder.html", top=top_3, details=festival_details)

@app.route("/festivals")
def festivals():
    with sqlite3.connect('fest.db') as con:
        cursor = con.cursor()
        festival_list = cursor.execute('SELECT * FROM festivals').fetchall()
        countries = cursor.execute('SELECT DISTINCT country FROM festivals').fetchall()
    return render_template('festivals.html', festivals=festival_list, countries=countries)

@app.route("/festivals/<int:festival_id>")
def festival_page(festival_id):
    if app.df is None:
        return redirect('/')
    else:
    # Render a festival page for each festival
        with sqlite3.connect('fest.db') as con:
            cursor = con.cursor()
            festival = cursor.execute('SELECT * FROM festivals WHERE id = ?', (festival_id,)).fetchone()
            headliners = cursor.execute('SELECT a.artist FROM lineups2025 l JOIN artists a ON l.artist_id = a.id WHERE festival_id = ? AND headliner = 1', (festival_id,)).fetchall()
            non_headliners = cursor.execute('SELECT a.artist FROM lineups2025 l JOIN artists a ON l.artist_id = a.id WHERE festival_id = ? AND headliner = 0', (festival_id,)).fetchall()
            headliner_data = {}
            non_headliner_data = {}
            # Find how many times the user has streamed each headline artist, store in a dictionary
            for headliner in headliners:
                headliner_data[headliner[0]] = len(app.df.loc[(app.df[ARTIST].str.upper() == headliner[0])])
            for non_headliner in non_headliners:
                non_headliner_data[non_headliner[0]] = len(app.df.loc[(app.df[ARTIST].str.upper() == non_headliner[0])])
            non_headliner_data = dict(sorted(non_headliner_data.items(), key=lambda item: item[1], reverse=True)[:5]) # Find top 5 non-headliners. ChatGPT & Stack Ex helped here with sorting the dictionary
        return render_template('festival_list.html', festival=festival, headliners=headliner_data, non_headliners=non_headliner_data)

@app.route("/artists", methods=['GET', 'POST'])
def search_artist():
    if request.method == 'POST':
        artist_request = request.form.get("artist_request")
        with sqlite3.connect('fest.db') as con:
            cursor = con.cursor()
            artist = cursor.execute("SELECT id, artist FROM artists WHERE artist = ?", (artist_request.upper(),)).fetchone()
    
    if artist:
        return redirect(f'/artists/{artist[0]}')
    else:
        return render_template('artist_missing.html'), 404

@app.route("/artists/<int:artist_id>")
def artist_page(artist_id):
    # Render a page for each artist   
    with sqlite3.connect('fest.db') as con:
        cursor = con.cursor()
        artist = cursor.execute('SELECT * FROM artists WHERE id = ?', (artist_id,)).fetchone()
        lineups = cursor.execute('SELECT l.festival_id, f.festival, l.headliner\
                                    FROM lineups2025 l\
                                    JOIN artists a ON l.artist_id = a.id\
                                    JOIN festivals f ON l.festival_id = f.id\
                                    WHERE l.artist_id = ?;', (artist_id,)).fetchall()
    
    if app.df is None:
        fig = None
    else:
        df_artist = app.df.loc[app.df[ARTIST].str.upper() == artist[1]]
    
        # Crosstab for counts of album streams per year for a certain artist
        artist_crosstab = pd.crosstab(df_artist['ts'].dt.year, df_artist[ALBUM])

        # Reset back to dataframe for plotly - ChatGPT assisted with .melt()
        stream_data = artist_crosstab.reset_index().melt(id_vars='ts', var_name=ALBUM, value_name='count')
        stream_data.rename(columns={'ts':'year', ALBUM:'album'}, inplace=True)
        fig = px.bar(stream_data, x="count", y="year", color='album', title="", orientation="h", color_discrete_sequence=app.colour_palette)
        fig.update_layout(plot_bgcolor='white')
        fig = pio.to_html(fig, full_html=False)

    return render_template('artist.html', artist=artist, lineups=lineups, fig=fig)

@app.route("/guide")
def guide():
    return render_template('guide.html')

if __name__ == '__main__':
    app.run(debug=True)
