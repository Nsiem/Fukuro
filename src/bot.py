from asyncio.windows_events import NULL
import os
import random
import discord
from PIL import Image
import PIL
import asyncio
from io import BytesIO
from malfunc import get_anime_list, get_anime_image, refreshtimer


from discord.ext import commands
from dotenv import load_dotenv



def main():
    loop = asyncio.get_event_loop()
    loop.create_task(refreshtimer())
    print("Fukuro-Sama is online!")
    bot.run(TOKEN)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='create-channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

@bot.command(name="searchAnime")
async def searchanime(ctx, *, search_query: str):
    aniquery = search_query.replace(" ", "%20")
    anime_list = await get_anime_list(aniquery, NULL)
    anime_img = await get_anime_image(anime_list['data'][0]['node']['main_picture']['medium'])
    anime_img.save('temp.jpg')

    title = anime_list['data'][0]['node']['title']
    await ctx.send(title, file=discord.File('temp.jpg'))
    os.remove('temp.jpg')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

   

if (__name__ == '__main__'):
    main()