import os
from typing import List, Dict
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
from dotenv import load_dotenv
from database import YouTubeDatabase
from datetime import datetime

# Load environment variables
load_dotenv()

class YouTubePlaylistCollector:
    def __init__(self):
        self.youtube = None
        self.credentials = None
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
        self.API_SERVICE_NAME = 'youtube'
        self.API_VERSION = 'v3'
        self.db = YouTubeDatabase()
        self.authenticate()

    def authenticate(self):
        """Authenticate with YouTube API using OAuth 2.0."""
        creds = None
        # Load credentials from token.pickle if it exists
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If credentials are not valid or don't exist, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secrets.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.credentials = creds
        self.youtube = build(self.API_SERVICE_NAME, self.API_VERSION, credentials=creds)

    def get_all_playlists(self) -> List[Dict]:
        """Get all playlists from the authenticated user's account and store in database."""
        playlists = []
        next_page_token = None

        while True:
            request = self.youtube.playlists().list(
                part="snippet,contentDetails",
                mine=True,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response['items']:
                playlist_data = {
                    'etag': item['etag'],
                    'id': item['id'],
                    'publishedAt': datetime.fromisoformat(item['snippet']['publishedAt'].replace('Z', '+00:00')),
                    'channelId': item['snippet']['channelId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'itemCount': item['contentDetails']['itemCount']
                }
                self.db.insert_playlist(playlist_data)
                playlists.append(playlist_data)

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        return playlists

    def get_playlist_videos(self, playlist_id: str) -> List[Dict]:
        """Get all videos from a specific playlist and store in database."""
        videos = []
        next_page_token = None

        while True:
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response['items']:
                # Store playlist item
                playlist_item_data = {
                    'etag': item['etag'],
                    'id': item['id'],
                    'playlistId': playlist_id,
                    'videoId': item['contentDetails']['videoId'],
                    'position': item['snippet']['position']
                }
                self.db.insert_playlist_item(playlist_item_data)

                # Get and store video details
                video_request = self.youtube.videos().list(
                    part="snippet",
                    id=item['contentDetails']['videoId']
                )
                video_response = video_request.execute()
                
                if video_response['items']:
                    video_item = video_response['items'][0]
                    video_data = {
                        'etag': video_item['etag'],
                        'id': video_item['id'],
                        'title': video_item['snippet']['title'],
                        'description': video_item['snippet']['description'],
                        'publishedAt': datetime.fromisoformat(video_item['snippet']['publishedAt'].replace('Z', '+00:00')),
                        'channelId': video_item['snippet']['channelId'],
                        'channelTitle': video_item['snippet']['channelTitle']
                    }
                    self.db.insert_video(video_data)
                    videos.append(video_data)

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        return videos

    def print_playlist_data(self):
        """Print all playlists and their videos from the database."""
        playlists = self.db.get_all_playlists()
        
        print(f"\nFound {len(playlists)} playlists:")
        print("-" * 50)

        for playlist in playlists:
            print(f"\nPlaylist: {playlist['title']}")
            print(f"Description: {playlist['description']}")
            print(f"Total videos: {playlist['itemCount']}")
            print("-" * 30)

            playlist_items = self.db.get_playlist_items(playlist['id'])
            for item in playlist_items:
                video = self.db.get_video(item['videoId'])
                if video:
                    print(f"Position {item['position']}: {video['title']}")
                    print(f"Video ID: {video['id']}")
                    print(f"Channel: {video['channelTitle']}")
                    print("-" * 20)

def main():
    collector = YouTubePlaylistCollector()
    playlists = collector.get_all_playlists()
    for playlist in playlists:
        collector.get_playlist_videos(playlist['id'])
    collector.print_playlist_data()

if __name__ == "__main__":
    main() 