import json
import boto3
from datetime import datetime
from io import StringIO
import pandas as pd 

def artist(data):
    artist_list = []
    for row in data['items']:
        for key, value in row.items():
            if key == "track":
                for artist in value['artists']:
                    artist_dict = {'artist_id':artist['id'], 'artist_name':artist['name'], 'spotify_url': artist['external_urls']['spotify']}
                    artist_list.append(artist_dict)
    return artist_list

def album(data):
    album_list = []
    for row in data['items']:
        album_id = row['track']['album']['id']
        album_name = row['track']['album']['name']
        album_release_date = row['track']['album']['release_date']
        album_total_tracks = row['track']['album']['total_tracks']
        album_url = row['track']['album']['external_urls']['spotify']
        album_element = {'album_id':album_id,'name':album_name,'release_date':album_release_date,
                            'total_tracks':album_total_tracks,'url':album_url}
        album_list.append(album_element)
    return album_list
    
def songs(data):
    song_list = []
    for row in data['items']:
        song_id = row['track']['id']
        song_name = row['track']['name']
        song_duration_mins = round((row['track']['duration_ms']/(60*1000)),2)
        song_url = row['track']['external_urls']['spotify']
        song_popularity = row['track']['popularity']
        song_added = row['added_at']
        album_id = row['track']['album']['id']
        artist_id = row['track']['album']['artists'][0]['id']
        song_element = {'song_id':song_id,'song_name':song_name,'duration_mins':song_duration_mins,'url':song_url,
                        'popularity':song_popularity,'song_added':song_added,'album_id':album_id,
                        'artist_id':artist_id
                       }
        song_list.append(song_element)
        
    return song_list
    
def lambda_handler(event, context):
    s3 = boto3.client('s3')
    
    #Data from api is stored in ths subfolder
    Bucket = "spotifyapidata"
    Key = "discover_weekly/raw_data/to_process/"
    
    spotify_data = []
    spotify_keys = []
    
    #s3.list_objects that take in the bucket name and prefix which is the key
    for file in s3.list_objects(Bucket=Bucket, Prefix=Key)['Contents']:
        file_key = file['Key']
        if file_key.split('.')[-1] == "json":
            response = s3.get_object(Bucket = Bucket, Key = file_key)
            content = response['Body']
            jsonObject = json.loads(content.read())
            
            spotify_data.append(jsonObject)
            spotify_keys.append(file_key)
            
    #Call the function to transform the data
            
    for data in spotify_data:
        album_list = album(data)
        artist_list = artist(data)
        song_list = songs(data)
        
        #Create dataframes
        
        album_df = pd.DataFrame(album_list)
        album_df = album_df.drop_duplicates(subset=['album_id'])
        
        artist_df = pd.DataFrame(artist_list)
        artist_df = artist_df.drop_duplicates(subset=['artist_id'])
        
        song_df = pd.DataFrame(song_list)
        
        #Convert dates to datetime
        
        album_df['release_date'] = pd.to_datetime(album_df['release_date'])
        song_df['song_added'] =  pd.to_datetime(song_df['song_added'])
        
        #Export the data into the respective files and folders
        songs_key = "discover_weekly/transformed_data/song_data/songs_transformed_" + str(datetime.now()) + ".csv"
        song_buffer=StringIO() #convert df into string like obje
        song_df.to_csv(song_buffer, index=False)
        song_content = song_buffer.getvalue()
        s3.put_object(Bucket=Bucket, Key=songs_key, Body=song_content)
        
        album_key = "discover_weekly/transformed_data/album_data/album_transformed_" + str(datetime.now()) + ".csv"
        album_buffer=StringIO()
        album_df.to_csv(album_buffer, index=False)
        album_content = album_buffer.getvalue()
        s3.put_object(Bucket=Bucket, Key=album_key, Body=album_content)
        
        artist_key = "discover_weekly/transformed_data/artist_data/artist_transformed_" + str(datetime.now()) + ".csv"
        artist_buffer=StringIO()
        artist_df.to_csv(artist_buffer, index=False)
        artist_content = artist_buffer.getvalue()
        s3.put_object(Bucket=Bucket, Key=artist_key, Body=artist_content)
        
    s3_resource = boto3.resource('s3')
    for key in spotify_keys:
        copy_source = {
            'Bucket': Bucket,
            'Key': key
        }
        
        #Copy the files from the source into the processed folder in the same bucket. Delete the file from to_process
        s3_resource.meta.client.copy(copy_source, Bucket, 'discover_weekly/raw_data/processed/' + key.split("/")[-1])    
        s3_resource.Object(Bucket, key).delete()
