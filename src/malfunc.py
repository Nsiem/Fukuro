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

# TESTER FUNCTION FOR TESTING ANIME SEARCHES OUTSIDE OF BOT
async def main():
    searchrequest = input("Please enter the title you wish to search: " )
    anime_img = await get_anime_image('https://api-cdn.myanimelist.net/images/anime/1412/107914.jpg')
    anime_img.show()
    # anime_list = await get_anime_list(searchrequest, NULL)
    # print(anime_list['data'])
    # while(1):
    #     nextsearchflag = input("Please enter 1 to see next page or 2 if you found what you are looking for: ")
    #     if(nextsearchflag == '2'):
    #         break
    #     else:
    #         print(anime_list['paging']['next'])
    #         anime_list = await get_anime_list(NULL, anime_list['paging']['next'])
    #         print(anime_list['data'])
    
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

# retrieves Image file from https link
async def get_anime_image(url: str):
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(url) as resp:
            anime_img = Image.open(BytesIO(await resp.read()))
            return anime_img

# retrieves specific anime info based on ID passed in
async def get_anime_info(aniID: str):
    url = f'https://api.myanimelist.net/v2/anime/{aniID}?fields=title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,media_type,status,genres,start_season,broadcast,source'
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(url) as resp:
            anime_info = await resp.json()
            return anime_info

# asyncio loop that call refresh() after set delay
# async def refreshtimer():
#     while True:
#         newtoken = refresh()
#         access_token = newtoken['access_token']
#         global header
#         header = {"Authorization": f'Bearer {access_token}'}
#         await asyncio.sleep(3500)

# start of file if main test function to be used
if __name__ == '__main__':
    asyncio.run(main())