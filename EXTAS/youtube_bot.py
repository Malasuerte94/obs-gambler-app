import os
import pickle
import time
import threading
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class YouTubeBot:
    def __init__(self, port=8080, channel_id="", commands=None):
        self.port = port
        self.channel_id = channel_id
        self.commands = commands or ["!referral"]
        self.running = False  # Flag to control bot execution
        self.stop_event = threading.Event()  # Event to signal stopping

    def get_authenticated_service(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', ['https://www.googleapis.com/auth/youtube.force-ssl'])
                creds = flow.run_local_server(port=self.port)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return build('youtube', 'v3', credentials=creds)

    def check_live_streams(self, youtube):
        request = youtube.search().list(
            part="snippet",
            channelId=self.channel_id,
            eventType="live",
            type="video"
        )
        response = request.execute()
        live_streams = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            live_streams.append({"videoId": video_id, "title": title})
        return live_streams

    def monitor_live_chat(self, youtube, live_chat_id):
        nextPageToken = None
        while not self.stop_event.is_set():  # Check the stop event
            try:
                request = youtube.liveChatMessages().list(
                    liveChatId=live_chat_id,
                    part="snippet,authorDetails",
                    pageToken=nextPageToken
                )
                response = request.execute()

                for item in response.get("items", []):
                    message_text = item["snippet"]["displayMessage"]
                    author_name = item["authorDetails"]["displayName"]
                    print(f"{author_name}: {message_text}")
                    for command in self.commands:
                        if message_text.startswith(command):
                            print(f"Command detected: {command} by {author_name}")
                            # Handle command logic here

                nextPageToken = response.get("nextPageToken")
                polling_interval = response.get("pollingIntervalMillis", 5000) / 1000
                time.sleep(polling_interval)
            except Exception as e:
                print(f"Error occurred: {e}")
                break

    def run(self):
        self.running = True
        self.stop_event.clear()  # Clear the stop event before starting
        youtube = self.get_authenticated_service()
        live_streams = self.check_live_streams(youtube)
        if not live_streams:
            print("No live streams found.")
            return
        for stream in live_streams:
            live_chat_id = self.get_live_chat_id(youtube, stream["videoId"])
            if live_chat_id:
                print(f"Monitoring live chat for stream: {stream['title']}")
                self.monitor_live_chat(youtube, live_chat_id)

    def stop(self):
        self.running = False
        self.stop_event.set()  # Signal the thread to stop
        print("Stopping bot...")

    def get_live_chat_id(self, youtube, video_id):
        request = youtube.videos().list(
            part="liveStreamingDetails",
            id=video_id
        )
        response = request.execute()
        return response["items"][0]["liveStreamingDetails"].get("activeLiveChatId")