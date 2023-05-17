import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import boto3
from datetime import datetime

def lambda_handler(event, context):
    ##Spotify API
    cilent_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')
    
    client_credentials_manager = SpotifyClientCredentials(client_id=cilent_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    
    ##Extract playlist data
    
    playlists = sp.user_playlists('spotify')
    playlist_link = "https://open.spotify.com/playlist/37i9dQZEVXcDYGt49X0ozW"
    playlist_URI = playlist_link.split("/")[-1].split("?")[0]
    
    spotify_data = sp.playlist_tracks(playlist_URI)   
    cilent = boto3.client('s3')
    filename = "spotify_raw_" + str(datetime.now()) + ".json"
    
    ## Save data into this folder
    cilent.put_object(
        Bucket="spotifyapidata",
        Key="discover_weekly/raw_data/to_process/" + filename,
        Body=json.dumps(spotify_data)
        )
