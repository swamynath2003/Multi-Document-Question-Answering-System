import re
import httpx
from typing import Optional, Dict
from datetime import datetime, timezone
from googleapiclient.discovery import build
import asyncio

class YouTubeQASystem:
    """System for answering questions about YouTube videos"""
    def __init__(self, youtube_api_key: str, openrouter_api_key: str):
        self.youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        self.openrouter_api_key = openrouter_api_key
        self.model_name = "mistralai/mistral-7b-instruct:free via OpenRouter"

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from various URL formats"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    async def get_video_info(self, video_id: str) -> Dict:
        """Get video metadata from YouTube API"""
        request = self.youtube.videos().list(part="snippet", id=video_id)
        response = request.execute()
        if not response.get('items'):
            raise ValueError(f"No video found with ID: {video_id}")
        return response['items'][0]
        
    async def process_video_with_openrouter(self, video_info, question):
        """Process video information and question using OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "HTTP-Referer": "https://askit-app.streamlit.app",
            "X-Title": "AskIt YouTube QA"
        }
        
        payload = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an AI assistant that provides concise answers to questions about YouTube videos based on their titles and descriptions."
                },
                {
                    "role": "user", 
                    "content": f"Video Title: {video_info['snippet']['title']}\nDescription: {video_info['snippet']['description']}\nQuestion: {question}"
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise ValueError(f"OpenRouter API Error: {response.text}")
            
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            
            return answer

    async def process_video(self, url: str, question: str) -> Dict[str, str]:
        """Process YouTube video URL and answer a question about it"""
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                raise ValueError("Invalid YouTube URL")

            video_info = await self.get_video_info(video_id)
            answer = await self.process_video_with_openrouter(video_info, question)
                
            return {
                "answer": answer,
                "video_title": video_info['snippet']['title'],
                "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                "thumbnail": video_info['snippet']['thumbnails']['high']['url'] if 'high' in video_info['snippet']['thumbnails'] else None
            }
        except Exception as e:
            return {"error": str(e)}