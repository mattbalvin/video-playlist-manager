import re
import os
from typing import List, Set, Dict
from youtube_playlist_collector import YouTubePlaylistCollector
from database import YouTubeDatabase

class FileImportTool:
    """
    Tool for importing YouTube video links from files and adding them to the database.
    Extracts links from plain text or Markdown format.
    """
    
    def __init__(self):
        """Initialize the file import tool with YouTube API connection and database."""
        self.youtube_collector = YouTubePlaylistCollector()
        self.db = YouTubeDatabase()
        
        # Regular expressions for extracting YouTube video links
        self.youtube_patterns = [
            # Raw URL pattern: https://www.youtube.com/watch?v=VIDEO_ID
            r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            
            # Markdown link pattern: [Title](https://www.youtube.com/watch?v=VIDEO_ID)
            r'\[.*?\]\(https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)\)'
        ]
    
    def extract_video_ids(self, file_path: str) -> Set[str]:
        """
        Extract YouTube video IDs from a file by processing line by line.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Set of unique YouTube video IDs found in the file
        """
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return set()
            
        video_ids = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Process the file line by line instead of loading the entire content
                for line in file:
                    # Apply all patterns to extract video IDs from this line
                    for pattern in self.youtube_patterns:
                        matches = re.findall(pattern, line)
                        video_ids.update(matches)
                    
            return video_ids
            
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return set()
    
    def process_file(self, file_path: str) -> List[Dict]:
        """
        Process a file to extract YouTube video IDs and add them to the database.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            List of video data dictionaries for newly added videos
        """
        video_ids = self.extract_video_ids(file_path)
        added_videos = []
        
        for video_id in video_ids:
            # Check if video already exists in the database
            existing_video = self.db.get_video(video_id)
            
            if not existing_video:
                print(f"Fetching new video data for ID: {video_id}")
                # Get video details from YouTube API
                video_data = self.get_video_data(video_id)
                
                if video_data:
                    # Add to database
                    self.db.insert_video(video_data)
                    added_videos.append(video_data)
                    
        return added_videos
    
    def process_files(self, file_paths: List[str]) -> List[Dict]:
        """
        Process multiple files to extract YouTube video IDs and add them to the database.
        
        Args:
            file_paths: List of paths to files to process
            
        Returns:
            List of video data dictionaries for newly added videos
        """
        all_added_videos = []
        
        for file_path in file_paths:
            added_videos = self.process_file(file_path)
            all_added_videos.extend(added_videos)
            
        return all_added_videos
    
    def get_video_data(self, video_id: str) -> Dict:
        """
        Get video data from the YouTube API.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing video data
        """
        try:
            # Use the YouTube API to get video details
            video_request = self.youtube_collector.youtube.videos().list(
                part="snippet",
                id=video_id
            )
            video_response = video_request.execute()
            
            if video_response['items']:
                video_item = video_response['items'][0]
                
                # Format data to match database schema
                from datetime import datetime
                video_data = {
                    'etag': video_item['etag'],
                    'id': video_item['id'],
                    'title': video_item['snippet']['title'],
                    'description': video_item['snippet']['description'],
                    'publishedAt': datetime.fromisoformat(video_item['snippet']['publishedAt'].replace('Z', '+00:00')),
                    'channelId': video_item['snippet']['channelId'],
                    'channelTitle': video_item['snippet']['channelTitle']
                }
                return video_data
            else:
                print(f"Video with ID {video_id} not found on YouTube")
                return None
                
        except Exception as e:
            print(f"Error fetching video data for ID {video_id}: {str(e)}")
            return None


def main():
    """Example usage of the FileImportTool."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python file_import_tool.py file1.txt [file2.txt ...]")
        sys.exit(1)
        
    file_paths = sys.argv[1:]
    
    importer = FileImportTool()
    added_videos = importer.process_files(file_paths)
    
    print(f"\nAdded {len(added_videos)} new videos to the database:")
    for video in added_videos:
        print(f" - {video['title']} (ID: {video['id']})")
    

if __name__ == "__main__":
    main()
