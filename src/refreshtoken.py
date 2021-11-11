import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

def refresh() -> dict:
    global CLIENT_ID, CLIENT_SECRET

    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': 'def5020075e68fdc18b79051cf40382773daa93eaa1135c123692b6e22d3665d3ab9238f37b8a2bc01c9c40b61ec1494b3eaf1188eb271b40528bbb14f5c42f7808aa7158740d620bf483e5b2bb0be8825136d1836cd78735857fcf8127f119bb7ab1dc34f2456cb4a4221e742c094ed329a122d325640256ab68cc09d64378b2ab37f826c10fa6afb040406338be5a77b6eb4732604bedf968c9341962a71a8d9d9c37404f773a70b91412f84a24da3191e53195ee58e0955a7062b2e024b2e73735d4ee5c457c9b12e98a85e15e34849156f90e3bc2f6e662fe4607d27083b9fa8b02eae5fe2a700d0e02df11339a76689b0b34ff0ffd438424cc485a1a7412cec7bc46dea8132265d47b404ba1c26ba9547abfb9ab8bd622f423f299491e2ea31b6f20bb0dd150a323872f876232224276f2b01fb3fcd06ee6d972d95ca1734d208dd1e0f44c2309dad28ece4f467f74c5c4ba41b3b9ea05de6fd92803716ba0ff81b1db415140b2acf6ef5f407a1cdae3bf772673a45d39ebafd654c1a4075e536518ca918ad'
    }

    response = requests.post(url, data)
    response.raise_for_status()  # Check whether the requests contains errors

    token = response.json()
    response.close()
    print('Token generated successfully!')

    with open('token.json', 'w') as file:
        json.dump(token, file, indent = 4)
        print('Token saved in "token.json"')

    return token



if __name__ == '__main__':
    token = refresh()
