# youtube_hot_word.py
def update_hotword_html(hotword, percent):
    """
    Create or update an HTML file "hot-word.html" that displays a card with a dark-green background
    and white text. The card shows:

        FIERBINTE: HOTWORD xx.x%

    where HOTWORD is displayed in uppercase and the percentage is colored on a gradient from blue (0%)
    to red (100%).

    Parameters:
        hotword (str or None): The hot word (if None, will be shown as "N/A").
        percent (float): The percentage of messages containing the hot word.
    """
    if hotword is None:
        hotword = "N/A"

    # Compute color for the percentage.
    # For percent=0 -> blue (#0000FF), percent=100 -> red (#FF0000)
    red = int(255 * (percent / 100))
    blue = int(255 * (1 - percent / 100))
    color_percent = f"rgb({red}, 0, {blue})"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Hot Word</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background-color: #222;
            color: white;
        }}
        .card {{
            background-color: darkgreen;
            padding: 20px;
            margin: 20px;
            border-radius: 8px;
            text-align: center;
            font-size: 2em;
        }}
        .hotword {{
            font-weight: bold;
        }}
        .percent {{
            color: {color_percent};
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="card">
        FIERBINTE: <span class="hotword">{hotword.upper()}</span>
        <span class="percent"> {percent:.1f}%</span>
    </div>
</body>
</html>
"""
    with open("hot-word.html", "w", encoding="utf-8") as f:
        f.write(html)


# For quick testing:
if __name__ == '__main__':
    update_hotword_html("test", 45.6)
    print("hot-word.html updated.")
