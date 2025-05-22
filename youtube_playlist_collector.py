import os
from typing import List, Dict
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class YouTubePlaylistCollector:
    def __init__(self):
        self.youtube = None
        self.credentials = None
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
        self.API_SERVICE_NAME = 'youtube'
        self.API_VERSION = 'v3'
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
        """Get all playlists from the authenticated user's account."""
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
                playlist = {
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'video_count': item['contentDetails']['itemCount']
                }
                playlists.append(playlist)

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        return playlists

    def get_playlist_videos(self, playlist_id: str) -> List[Dict]:
        """Get all videos from a specific playlist."""
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
                video = {
                    'id': item['contentDetails']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'position': item['snippet']['position']
                }
                videos.append(video)

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        return videos

    def print_playlist_data(self):
        """Print all playlists and their videos."""
        playlists = self.get_all_playlists()
        
        print(f"\nFound {len(playlists)} playlists:")
        print("-" * 50)

        for playlist in playlists:
            print(f"\nPlaylist: {playlist['title']}")
            print(f"Description: {playlist['description']}")
            print(f"Total videos: {playlist['video_count']}")
            print("-" * 30)

            videos = self.get_playlist_videos(playlist['id'])
            for video in videos:
                print(f"Position {video['position']}: {video['title']}")
                print(f"Video ID: {video['id']}")
                print("-" * 20)

def main():
    collector = YouTubePlaylistCollector()
    collector.print_playlist_data()

if __name__ == "__main__":
    main() 