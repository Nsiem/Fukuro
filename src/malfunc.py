from asyncio.windows_events import NULL
import aiohttp
import asyncio
import json
from PIL import Image
from io import BytesIO
from refreshtoken import refresh

with open('token.json') as t:
    tokens = json.load(t)

access_token = tokens['access_token']
refresh_token = tokens['refresh_token']
header = {"Authorization": f'Bearer {access_token}'}

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
    

async def get_anime_list(searchQuery: str, customurl: str) -> json:
    url = f'https://api.myanimelist.net/v2/anime?q={searchQuery}&limit=5'
    async with aiohttp.ClientSession(headers=header) as session:
        if (customurl != NULL):
            url = customurl
        async with session.get(url) as resp:
            anime_list = await resp.json()
    session.close
    return anime_list

async def get_anime_image(url: str):
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(url) as resp:
            anime_img = Image.open(BytesIO(await resp.read()))
            return anime_img

async def refreshtimer():
    while True:
        refresh()
        await asyncio.sleep(1800)

if __name__ == '__main__':
    asyncio.run(main())