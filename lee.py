from flask import Flask,jsonify
import requests
import time
import json

app = Flask(__name__)

@app.route("/")
def home():
    # grab info from the reddit homepage (the json version)
    uri = "https://www.reddit.com/.json"
    try:
        requestResponse = requests.get(uri, headers={'User-agent': 'leebot 0.1'})
    except requests.ConnectionError:
        sys.exit(1)

    requestResult = json.loads(requestResponse.text)
    items = requestResult[u'data'][u'children']
    bottomContentScore = 0
    results = {}
    for i in range(0, len(items)):
        reddit = items[i][u'data']
        if 'post_hint' in reddit and reddit['post_hint'] == 'image':
            # let's define popularity as the number of comments divided by the age of the content
            # so if something is 10 seconds old, and has 100 comments, we'd say that is more popular
            # than something that is 100 seconds old that only has 1 cmment
            age = (int(time.time()) - int(reddit['created_utc']))
            popularity = reddit['num_comments'] / age
            # then we will say something has a top content score based on ups * popularity.
            topContent = int(popularity * reddit['ups'])

            results[i] = {}
            results[i].update(
                {'title': reddit['title'], 'link' : reddit['url'], 'ups': reddit['ups'], 'created': reddit['created'], 'popularity': popularity,
                 'topScore': topContent, 'isTop': False})

        else:
            # we could probably check for animated gifs and other stuff. Maybe later
            continue

    bottomContent = min((x['topScore'], x) for x in results.values())[1]
    lowestScore = bottomContent['topScore']

    for key, value in results.items():
        # Arbitrary, but lets say something it top content if it has a topScore higher than 4X the lowest score 
        if results[key]['topScore'] > lowestScore * 4:
            results[key]['isTop'] = True

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug = True)