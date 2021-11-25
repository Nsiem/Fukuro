import json
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
with open('token.json') as t:
    tokens = json.load(t)

REFRESH_TOKEN = tokens['refresh_token']

# Simple function to refresh tokens in token.json for uninterupted use
def refresh():
    global CLIENT_ID, CLIENT_SECRET

    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN
    }

    response = requests.post(url, data)
    response.raise_for_status()

    token = response.json()
    response.close()

    with open('token.json', 'w') as file:
        json.dump(token, file, indent = 4)

    return token


if __name__ == '__main__':
    refresh()
