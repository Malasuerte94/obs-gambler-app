# youtube_hot_word.py
def update_hotword_html(hotword, percent, top3=None):
    """
    Create or update an HTML file "hot-word.html" that displays a card.
    If top3 is provided (a list of (word, percent) tuples), it displays the top three words.
    Otherwise, it displays the single hot word and percentage.
    """
    if top3:
        rows = ""
        for w, p in top3:
            red = int(255 * (p / 70))
            blue = int(255 * (1 - p / 70))
            color = f"rgb({red}, 0, {blue})"
            rows += f"<div><span class='hotword'>{w.upper()}</span> <span class='percent' style='color:{color};'>{p:.1f}%</span></div>\n"
        card_content = rows
    else:
        if hotword is None:
            hotword = "N/A"
        red = int(255 * (percent / 70))
        blue = int(255 * (1 - percent / 70))
        color = f"rgb({red}, 0, {blue})"
        card_content = f"<span class='hotword'>{hotword.upper()}</span> <span class='percent'>{percent:.1f}%</span>"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="2">
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
            background-color: rgba(0, 49, 0, 0.76);
            padding: 20px;
            margin: 20px;
            border-radius: 8px;
            text-align: center;
            font-size: 1.7em;
            display: flex;
            flex-direction: column;
            gap: 10px;
            justify-content: center;
            align-items: center;
        }}
        .hotword {{
            font-weight: bold;
        }}
        .percent {{
            color: {color};
            font-weight: bold;
            text-shadow:
               1px 1px 0 #FFFFFF,
             -1px -1px 0 #FFFFFF,  
              1px -1px 0 #FFFFFF,
              -1px 1px 0 #FFFFFF,
               1px 1px 0 #FFFFFF;
        }}
    </style>
</head>
<body>
    <div class="card">
        <span>HOT WORDS</span>
        {card_content}
    </div>
</body>
</html>
"""
    with open("hot-word.html", "w", encoding="utf-8") as f:
        f.write(html)
