from flask import Flask
import requests

app = Flask(__name__)

@app.route('/')
def show_meme():
    url = "https://meme-api.com/gimme/wholesomememes"
    response = requests.request("GET", url)
    meme = response.json()

    meme_url = meme["url"]
    title = meme["title"]
    subreddit = meme["subreddit"]

    return f"""
    <html>
    <head>
        <title>Memes'R'Us</title>
        <meta charset="UTF-8" name="viewport" content="width=device-width, initial-scale=0.8">
        <meta http-equiv="refresh" content="10; url=http://127.0.0.1:5000" />
    </head>

    <body style="text-align:center; font-family:Arial;">
        <h1>{title}</h1>
        <img src="{meme_url}" style="max-width:500px; border-radius:10px;"><br><br>
        <p>Source subreddit: <b>r/{subreddit}</b></p>
        <p><i>Refreshing every 10 seconds...</i></p>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)
