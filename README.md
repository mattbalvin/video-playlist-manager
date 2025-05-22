# YouTube Playlist Collector

A Python module to collect and display YouTube playlist data from your YouTube account.

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up YouTube API credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the YouTube Data API v3
   - Create OAuth 2.0 credentials
   - Download the credentials and save them as `client_secrets.json` in the project directory

## Usage

Run the script:
```bash
python youtube_playlist_collector.py
```

The first time you run the script, it will:
1. Open your default web browser
2. Ask you to log in to your Google account
3. Request permission to access your YouTube data
4. Save the authentication token for future use

The script will then:
- Fetch all your playlists
- For each playlist, fetch all videos
- Print a formatted list of playlists and their videos

## Features

- OAuth 2.0 authentication
- Automatic token refresh
- Pagination support for large playlists
- Detailed video information including position in playlist
- Cached credentials for faster subsequent runs
