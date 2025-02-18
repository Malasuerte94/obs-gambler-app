import requests
from utils.environment import is_dev

# Replace with your actual API key if needed.
STOP_WORDS = {"și", "la", "si", "de", "in", "în", "pe", "el", "e", "ai", "eu", "cu", "ca", "rotiri", "gratuite", "fara", "depunere", "ala"}

def get_live_video_id(yt_channel, api_key):
    if is_dev():
        return 'FuhKzvvFGvo'
    else:
        # if mode is dev
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


def analyze_hotword(chat_messages):
    """Analyze chat messages and return the most frequent hotword."""
    messages = chat_messages[-200:] if len(chat_messages) >= 200 else chat_messages[-100:]
    word_occurrence = {}

    for msg in messages:
        words = {w for w in msg.lower().split() if len(w) > 1 and w not in STOP_WORDS}
        for w in words:
            word_occurrence[w] = word_occurrence.get(w, 0) + 1

    # Find the most common word (must appear in at least 5 messages)
    candidates = {w: cnt for w, cnt in word_occurrence.items() if cnt >= 2}
    if not candidates:
        return None, 0.0

    hotword = max(candidates, key=lambda w: candidates[w])

    # Calculate percentage of messages containing the hotword
    count = sum(1 for msg in messages if hotword in msg.lower())
    percent = (count / len(messages)) * 100

    return hotword, percent


def analyze_top_words(chat_messages, top_n=3):
    """Analyze chat messages and return the top_n most frequent words."""
    messages = chat_messages[-200:] if len(chat_messages) >= 200 else chat_messages[-100:]
    word_occurrence = {}

    for msg in messages:
        try:
            words = {w for w in msg.lower().split() if len(w) > 1 and w not in STOP_WORDS}
            for w in words:
                word_occurrence[w] = word_occurrence.get(w, 0) + 1

        except Exception as e:
            print(f"Error processing message: '{msg}', Error: {e}")
            continue  # Skip problematic messages

    # Find the most common words (must appear in at least 2 messages)
    candidates = {w: cnt for w, cnt in word_occurrence.items() if cnt >= 2}
    if not candidates:
        return []

    sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)

    top_words = []
    for w, cnt in sorted_candidates[:top_n]:
        try:
            count = sum(1 for msg in messages if w in msg.lower())
            percent = (count / len(messages)) * 100
            top_words.append((w, percent))
        except Exception as e:
            print(f"Error processing word '{w}': {e}")
            continue

    return top_words


