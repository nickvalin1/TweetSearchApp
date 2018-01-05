from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
import base64
import json
from bottle import route, run, template, view, TEMPLATE_PATH, request
from xml.dom import minidom
import re


def authenticate():
    url = "https://api.twitter.com/oauth2/token"
    params = {"grant_type": "client_credentials"}
    bearer_token = "F6fFiGEXgeROAYC9olBWq6m19:wI0T1qWfR806iY5Cqltw3c3pHNMr3m4dRclHblsd8Morsl6mzJ"
    encoded_token = base64.b64encode(bearer_token.encode("ascii"))
    request = Request(url)
    request.add_header("Content-Type", "application/x-www-form-urlencoded;charset=UTF-8")
    request.add_header("Authorization", "Basic %s" % encoded_token.decode("UTF-8"))
    request.data = urlencode(params).encode()
    response = urlopen(request).read().decode()
    access_token = json.loads(response)["access_token"]
    return access_token


def get_tweets(username):
    url = "https://api.twitter.com/1.1/search/tweets.json"
    query = "from:" + username
    url += "?q=" + query + "&count=5"
    request = Request(url)
    request.add_header("Authorization", "Bearer %s" % authenticate())
    try:
        response = urlopen(request).read().decode()
    except HTTPError as e:
        print(e.read())
    tweet_data = json.loads(response)
    tweets = []
    for i in range(5):
        tweet = dict()
        tweet["text"] = tweet_data["statuses"][i]["text"]
        tweet["time"] = tweet_data["statuses"][i]["created_at"]
        tweet["words"] = num_words(tweet_data["statuses"][i]["text"])
        tweets.append(tweet)
    return tweets


def check_if_word(word):
    url = "https://www.dictionaryapi.com/api/v1/references/collegiate/xml/" + word + \
          "?key=d27b313d-a706-4533-bb8f-a008082e284c"
    response = urlopen(url).read()
    try:
        xml = minidom.parseString(response)
    except Exception as e:
        print(e)
        print(word)
        print(response)
    entry = xml.getElementsByTagName("entry")
    if len(entry) > 0:
        return True
    else:
        return False


def num_words(tweet):
    sanitized_tweet = re.sub("[^\s\w\d\-']", "", tweet)
    print(tweet)
    print(sanitized_tweet)
    words = sanitized_tweet.split()
    count = 0
    for word in words:
        if check_if_word(word):
            count += 1
    return count

TEMPLATE_PATH.insert(0, "views")


@route("/")
@route("/<username>")
@view("index")
def greet(username=None):
    if username:
        tweets = get_tweets(username)
    else:
        tweets = None
    return dict(tweets=tweets)


run(host="localhost", port=8080, debug=True)
