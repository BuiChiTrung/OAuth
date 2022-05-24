from dotenv import load_dotenv
import json
import requests
import os

from auth_decorator import login_required
from flask import Flask, redirect, render_template, url_for, session
from authlib.integrations.flask_client import OAuth

load_dotenv()
app = Flask(__name__)
# MUST have this line
app.secret_key = os.getenv('APP_SECRET_KEY')

# OAuth Setup
oauth = OAuth(app)

# Some param here can be load from app.config too
google = oauth.register(
    name='google',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'email profile https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/drive.readonly'},
)
google = oauth.create_client('google')


@app.route('/')
@login_required
def index():
    email = dict(session)['profile']['email']
    return render_template('index.html', user_info=session['profile'])


@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    # Get access token from google
    token = google.authorize_access_token()  
    session['access_token'] = token['access_token']
    resp = google.get('userinfo', token=token)  
    user_info = resp.json()
    print(user_info, "hahahahahaha")
    
    session['profile'] = user_info
    return redirect('/')


@app.route('/drive/files')
def get_files():
    url = "https://www.googleapis.com/drive/v3/files"
    headers = {
        'Authorization': 'Bearer {}'.format(session['access_token'])
    }
    response = json.loads(requests.request("GET", url, headers=headers, data={}).text)
  
    return render_template('drive_files.html', files=response['files'])


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

if __name__ == '__main__':
    app.run(port=5001, debug=True)

