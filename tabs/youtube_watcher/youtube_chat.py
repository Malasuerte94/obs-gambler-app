import requests

# Replace with your actual API key if needed.
YOUTUBE_DATA_VIEW = "##"

def get_live_video_id(channel_id, api_key=YOUTUBE_DATA_VIEW):
    """
    Check if the given channel is live and return the live video ID.
    If no live stream is found, returns None.
    """
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelId": channel_id,
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
    """
    Analyze the provided chat messages (a list of strings) and return the "hot word"
    along with the percentage of the last 200 messages that contain that word.

    A word is only considered if it appears in at least 5 messages.
    Common stopwords are filtered out and words with 1 character are ignored.
    The analysis is case-insensitive.

    Returns:
        (hotword, percent) tuple, or (None, 0.0) if no candidate exists.
    """
    # Use only the last 200 messages.
    messages = chat_messages[-200:] if len(chat_messages) > 200 else chat_messages

    # Count occurrence of each unique word (converted to lowercase) per message.
    word_occurrence = {}
    for msg in messages:
        # Split message into words and ignore those with 1 character.
        words = {w for w in msg.lower().split() if len(w) > 1}
        for w in words:
            word_occurrence[w] = word_occurrence.get(w, 0) + 1

    # Filter words that appear in at least 5 messages.
    candidates = {w: cnt for w, cnt in word_occurrence.items() if cnt >= 5}
    if not candidates:
        return None, 0.0

    # Define a set of common stopwords (all in lowercase).
    stopwords = {"și", "la", "si", "de", "in", "în", "pe", "el", "e", "ai", "eu", "cu", "ca"}

    # Filter out stopwords from candidates.
    non_stop_candidates = {w: cnt for w, cnt in candidates.items() if w not in stopwords}

    # If non-stopword candidates exist, choose the one with the highest count;
    # otherwise, fall back to using the full candidate dictionary.
    if non_stop_candidates:
        hotword = max(non_stop_candidates, key=lambda w: non_stop_candidates[w])
    else:
        hotword = max(candidates, key=lambda w: candidates[w])

    # Count in how many messages (of the last 200) the hotword appears.
    count = sum(1 for msg in messages if hotword in msg.lower())
    percent = (count / len(messages)) * 100
    return hotword, percent





