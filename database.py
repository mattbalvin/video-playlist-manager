import sqlite3
from datetime import datetime
from typing import Dict, List
import json

class YouTubeDatabase:
    def __init__(self, db_path: str = "youtube_data.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize_database()

    def connect(self):
        """Establish connection to the SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def initialize_database(self):
        """Create the database tables if they don't exist."""
        self.connect()
        
        # Create playlist table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlist (
            etag TEXT,
            id TEXT PRIMARY KEY,
            publishedAt DATETIME,
            channelId TEXT,
            title TEXT,
            description TEXT,
            itemCount INTEGER
        )
        ''')

        # Create playlist_item table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlist_item (
            etag TEXT,
            id TEXT PRIMARY KEY,
            playlistId TEXT,
            videoId TEXT,
            position INTEGER,
            FOREIGN KEY (playlistId) REFERENCES playlist (id)
        )
        ''')

        # Create video table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS video (
            etag TEXT,
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            publishedAt DATETIME,
            channelId TEXT,
            channelTitle TEXT
        )
        ''')

        self.conn.commit()
        self.close()

    def insert_playlist(self, playlist_data: Dict):
        """Insert or update a playlist record."""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO playlist 
            (etag, id, publishedAt, channelId, title, description, itemCount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                playlist_data.get('etag'),
                playlist_data.get('id'),
                playlist_data.get('publishedAt'),
                playlist_data.get('channelId'),
                playlist_data.get('title'),
                playlist_data.get('description'),
                playlist_data.get('itemCount')
            ))
            self.conn.commit()
        finally:
            self.close()

    def insert_playlist_item(self, item_data: Dict):
        """Insert or update a playlist item record."""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO playlist_item 
            (etag, id, playlistId, videoId, position)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                item_data.get('etag'),
                item_data.get('id'),
                item_data.get('playlistId'),
                item_data.get('videoId'),
                item_data.get('position')
            ))
            self.conn.commit()
        finally:
            self.close()

    def insert_video(self, video_data: Dict):
        """Insert or update a video record."""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO video 
            (etag, id, title, description, publishedAt, channelId, channelTitle)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_data.get('etag'),
                video_data.get('id'),
                video_data.get('title'),
                video_data.get('description'),
                video_data.get('publishedAt'),
                video_data.get('channelId'),
                video_data.get('channelTitle')
            ))
            self.conn.commit()
        finally:
            self.close()

    def get_all_playlists(self) -> List[Dict]:
        """Retrieve all playlists from the database."""
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM playlist')
            columns = [description[0] for description in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        finally:
            self.close()

    def get_playlist_items(self, playlist_id: str) -> List[Dict]:
        """Retrieve all items for a specific playlist."""
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM playlist_item WHERE playlistId = ?', (playlist_id,))
            columns = [description[0] for description in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        finally:
            self.close()

    def get_video(self, video_id: str) -> Dict:
        """Retrieve a specific video by ID."""
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM video WHERE id = ?', (video_id,))
            columns = [description[0] for description in self.cursor.description]
            row = self.cursor.fetchone()
            return dict(zip(columns, row)) if row else None
        finally:
            self.close() 