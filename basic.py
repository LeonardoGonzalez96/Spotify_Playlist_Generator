from flask import Flask, render_template, url_for, flash, redirect, request, session
from forms import ArtistForm, RegistrationForm, LoginForm
from flask_behind_proxy import FlaskBehindProxy
from list_songs import api_call, json_to_dataframe, top_songs_call
from genius import get_lyrics
from make_album import create_playlist
from mp3 import download_songs
import pandas as pd
import functools
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


x=''
id_name_dict = {}
app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = '626423b656a4f6851a5cbece30f78108'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    playlist_ids = db.Column(db.String(), nullable=True)
    playlist_names = db.Column(db.String(), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
migrate = Migrate(app, db)

def is_logged_in():
    return 'username' in session

def require_login(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if not is_logged_in():
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped_view

@app.before_request
def check_login():
    if not is_logged_in() and request.endpoint != 'static' and request.endpoint != 'login' and request.endpoint != 'register':
        return redirect(url_for('login'))

@app.before_request
def logout_on_close():
    if not request.referrer:
        session.clear()

@app.route("/")
@app.route("/home")
def home():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('home.html', subtitle='Home', text='This is the home page')

@app.route("/about")
def about():
   return render_template('about.html', text="This is the about page.", title = 'About Page')

@app.route("/spotify-generator", methods=['GET', 'POST'])
@require_login
def spotify_generator():
    return render_template('spotify_generator.html', title='Spotify Playlist Generator')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username is already taken. Please choose a different one.', 'danger')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Login successful.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
songs = None
playlist_name = None
@app.route('/success', methods=['GET', 'POST'])
@require_login
def playlist_created():
    form = ArtistForm()
    global songs
    global playlist_name
    global x
    global id_name_dict
    if request.method == "POST":
        artist_name = request.form.get('artist')
        username = request.form.get('username')
        playlist_name = request.form.get('playlist')
        dat = api_call(artist_name)
        adf = json_to_dataframe(dat)
        rel_artists = adf['name'].tolist()
        songs = pd.DataFrame()
        for ar in rel_artists[:5]:
            ar_songs = top_songs_call(ar)
            ar_songs_df = pd.DataFrame(ar_songs)
            songs = pd.concat([songs, ar_songs_df])
        # set_songs_df(songs)
        # get_genius_info()1
        print('songs:', songs)
        # song_ids = songs['track_id'].to_list()
        song_names = songs['song'].to_list()
        # print(song_ids)
        x = create_playlist(username, playlist_name, songs)
        
        flash(f"Playlist '{playlist_name}' created successfully with {len(songs)} songs.", 'success')

        ###added
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if user:
            if user.playlist_ids and user.playlist_names:
                user.playlist_ids += f',{x}'
                user.playlist_names += f',{playlist_name}'
            else:
                user.playlist_ids = str(x)
                user.playlist_names = str(playlist_name)
            db.session.commit()
        else:
            flash('User not found.', 'danger')
        ###added

        track_ids = songs['track_id'].tolist()
        id_name_dict = {track_ids[i]: song_names[i] for i in range(len(track_ids))}
        print(id_name_dict)
        
        ###added
        return render_template('success.html', title='Playlist Created', playlist_id=x, track_ids=track_ids, username=username, songs=songs, playlist_name=playlist_name)
        ###added

@app.route('/download-songs', methods=['POST'])
@require_login
def download_route():
    global songs
    global playlist_name
    download_songs(songs, playlist_name)
    return {"message": "Songs downloaded"}

@app.route('/account')
@require_login
def account():
    username = session['username']
    user = User.query.filter_by(username=username).first()
    if user and user.playlist_ids:
        playlist_ids = user.playlist_ids.split(',')
        playlist_names = user.playlist_names.split(',') if user.playlist_names else []
    else:
        playlist_ids = []
        playlist_names = []
    return render_template('account.html', title='Account', username=username, playlist_ids=playlist_ids, playlist_names=playlist_names)

  

@app.route("/get-lyrics", methods=['GET', 'POST'])
def getLyrics():
   if request.method == "POST":
      song_id = request.form.get('id')
      print(song_id)
      song_name = id_name_dict[song_id]
      name, lyrics = get_lyrics(song_name)
      print(lyrics)
      to_return = [name, lyrics]
      return to_return

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")
#. ~/.bashrc
