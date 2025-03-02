import requests
from utils.environment import is_dev

# Replace with your actual API key if needed.
STOP_WORDS = {"și", "la", "si", "de", "in", "în", "pe", "el", "e", "ai", "eu", "cu", "ca", "rotiri", "gratuite", "fara", "depunere", "ala"}

def get_live_video_id(yt_channel, api_key):
    if is_dev():
        return 'NIYOTPN-KKs'
    else:
        """
        Check if the given channel is live and return the live video ID.
        If no live stream is found, returns None.
        """
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "channelId": yt_channel,
            "eventType": "live",
            "type": "video",
            "key": api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        if items:
            return items[0]["id"]["videoId"]
        return None


def analyze_hot_message(chat_messages):
    """
    Analyze chat messages and return the single most frequently repeated message
    ("hot message") and the percentage of messages that match it.
    """
    # Use the last 200 messages if available, else the last 100.
    messages = chat_messages[-200:] if len(chat_messages) >= 200 else chat_messages[-100:]
    message_occurrence = {}

    # Count frequency based on a normalized (lowercase and stripped) version of the message.
    for msg in messages:
        normalized = msg.strip().lower()
        message_occurrence[normalized] = message_occurrence.get(normalized, 0) + 1

    # Consider only messages that appear at least 2 times.
    candidates = {m: count for m, count in message_occurrence.items() if count >= 2}
    if not candidates:
        return None, 0.0

    # Find the most frequent message.
    hot_message_normalized = max(candidates, key=lambda m: candidates[m])
    count = candidates[hot_message_normalized]
    percent = (count / len(messages)) * 100

    # Retrieve the original version (with original case) from messages.
    for msg in messages:
        if msg.strip().lower() == hot_message_normalized:
            return msg, percent

    return None, 0.0


def analyze_top_messages(chat_messages, top_n=3):
    """
    Analyze chat messages and return the top_n most frequently repeated messages.
    Each item in the returned list is a tuple: (message, percentage)
    """
    messages = chat_messages[-200:] if len(chat_messages) >= 200 else chat_messages[-100:]
    message_occurrence = {}

    for msg in messages:
        normalized = msg.strip().lower()
        message_occurrence[normalized] = message_occurrence.get(normalized, 0) + 1

    # Only consider messages that appear at least twice.
    candidates = {m: count for m, count in message_occurrence.items() if count >= 2}
    if not candidates:
        return []

    # Sort messages by frequency in descending order.
    sorted_candidates = sorted(candidates.items(), key=lambda item: item[1], reverse=True)
    top_messages = []

    for normalized_msg, count in sorted_candidates[:top_n]:
        percent = (count / len(messages)) * 100
        # Retrieve the original version from the messages list.
        for msg in messages:
            if msg.strip().lower() == normalized_msg:
                top_messages.append((msg, percent))
                break

    return top_messages


