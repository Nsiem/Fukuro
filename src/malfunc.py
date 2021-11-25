from asyncio.windows_events import NULL
import aiohttp
import asyncio
import json
from PIL import Image
from io import BytesIO
from refreshtoken import refresh

with open('token.json') as t:
    tokens = json.load(t)

ACCESS_TOKEN = tokens['access_token']

header = {"Authorization": f'Bearer {ACCESS_TOKEN}'}
    
# Retrieves anime list based on text search, returns json with up to 5 results at a time
async def get_anime_list(searchQuery: str, customurl: str):
    url = f'https://api.myanimelist.net/v2/anime?q={searchQuery}&limit=5'
    async with aiohttp.ClientSession(headers=header) as session:
        if (customurl != NULL):
            url = customurl
        async with session.get(url) as resp:
            anime_list = await resp.json()
    session.close
    return anime_list

# retrieves specific anime info based on ID passed in
async def get_anime_info(aniID: str):
    url = f'https://api.myanimelist.net/v2/anime/{aniID}?fields=title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,media_type,status,genres,start_season,broadcast,source'
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(url) as resp:
            anime_info = await resp.json()
            return anime_info


# Retrieves manga list based on text search, returns json with up to 5 results at a time
async def get_manga_list(searchQuery: str, customurl: str):
    url = f'https://api.myanimelist.net/v2/manga?q={searchQuery}&limit=5'
    async with aiohttp.ClientSession(headers=header) as session:
        if (customurl != NULL):
            url = customurl
        async with session.get(url) as resp:
            manga_list = await resp.json()
    session.close
    return manga_list

# retrieves specific manga info based on ID passed in
async def get_manga_info(mangaID: str):
    url = f'https://api.myanimelist.net/v2/manga/{mangaID}?fields=title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,status,genres'
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(url) as resp:
            manga_info = await resp.json()
            return manga_info

# asyncio loop that call refresh() after set delay
# async def refreshtimer():
#     while True:
#         newtoken = refresh()
#         access_token = newtoken['access_token']
#         global header
#         header = {"Authorization": f'Bearer {access_token}'}
#         await asyncio.sleep(3500)