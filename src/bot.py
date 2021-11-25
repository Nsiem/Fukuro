from asyncio.windows_events import NULL
import os
import discord
from PIL import Image
import asyncio
from discord import colour
from discord.embeds import Embed, EmptyEmbed
from discord.ext.commands.errors import ExpectedClosingQuoteError
from malfunc import *
from discord.ext import commands
from dotenv import load_dotenv


# Main start of program, begins asyncio loop to refresh token regardless of access every set amount of time
def main():
    # loop = asyncio.get_event_loop()
    # loop.create_task(refreshtimer())
    print("Fukuro-Sama is online!")
    bot.run(TOKEN)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='f!')

# generates string containing the anime/manga titles from text search, to be put in embed
def jsontitles(Alist):
    animetitles = ""
    for i in range(len(Alist['data'])):
        animetitles = animetitles + f"{i+1}. {Alist['data'][i]['node']['title']}\n"
    animetitles = animetitles + "\n0. Next page"
    return animetitles

# Generates and returns discord.Embed containing all info regarding anime search made by user
def anime_info_embed(Ainfo):
    synopsis = Ainfo['synopsis'][:-24]
    result = discord.Embed(title = f"{Ainfo['title']}", description = synopsis, colour = discord.Colour.blue())
    result.set_image(url=Ainfo['main_picture']['large'])
    result.set_author(name='Fukuro', icon_url='https://i.postimg.cc/Y28MqWsg/sus.png')
    result.set_thumbnail(url='https://i.postimg.cc/Y28MqWsg/sus.png')
    result.add_field(name='__Japanese Title:__', value=Ainfo['alternative_titles']['ja'])
    if (Ainfo['status'] != 'not_yet_aired'):
        try:
            result.add_field(name='__Aired:__', value=f"{Ainfo['start_season']['season'].title()} {Ainfo['start_season']['year']}")
            result.add_field(name='__MAL score:__', value=Ainfo['mean'])
            result.add_field(name='__MAL rank:__', value=f"#{Ainfo['rank']}")
        except KeyError:
            pass
    result.add_field(name='__Status:__', value=Ainfo['status'].replace("_", " ").title())
    genres = ''
    for i in range(len(Ainfo['genres']) - 1):
        genres += f"{Ainfo['genres'][i]['name']}, "
    genres += Ainfo['genres'][-1]['name']
    result.add_field(name='__Genres:__', value=genres)
    result.set_footer(text='Information provided by MyAnimeList.net', icon_url='https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png')
    return result

# Generates and returns discord.Embed containing all info regarding manga search made by user
def manga_info_embed(Minfo):
    synopsis = Minfo['synopsis'][:-24]
    result = discord.Embed(title = f"{Minfo['title']}", description = synopsis, colour = discord.Colour.dark_red())
    result.set_image(url=Minfo['main_picture']['large'])
    result.set_author(name='Fukuro', icon_url='https://i.postimg.cc/Y28MqWsg/sus.png')
    result.set_thumbnail(url='https://i.postimg.cc/Y28MqWsg/sus.png')
    result.add_field(name='__Japanese Title:__', value=Minfo['alternative_titles']['ja'])
    if (Minfo['status'] != 'not_yet_published'):
        try:
            result.add_field(name='__Publishing Start:__', value=f"{Minfo['start_date']}")
            result.add_field(name='__MAL score:__', value=Minfo['mean'])
            result.add_field(name='__MAL rank:__', value=f"#{Minfo['rank']}")
        except KeyError:
            pass
    result.add_field(name='__Status:__', value=Minfo['status'].replace("_", " ").title())
    genres = ''
    for i in range(len(Minfo['genres']) - 1):
        genres += f"{Minfo['genres'][i]['name']}, "
    genres += Minfo['genres'][-1]['name']
    result.add_field(name='__Genres:__', value=genres)
    result.set_footer(text='Information provided by MyAnimeList.net', icon_url='https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png')
    return result


# Bot command to begin search of information on select anime, and completes with either timeout, or anime info
@bot.command(name="animeinfo")
async def searchanime(ctx, *, search_query: str):
    aniquery = search_query.replace(" ", "%20")
    anime_list = await get_anime_list(aniquery, NULL)
    animetitles = jsontitles(anime_list)
    animeresults = discord.Embed(title = "Did you mean?...", colour = discord.Colour.blue())
    animeresults.add_field(name = "Anime:", value = animetitles)
    animeresults.set_footer(text="Please type the number of your anime")

    message = await ctx.send(embed=animeresults)

    def check(m):
            if(m.author == ctx.author):
                if(m.content == '1' or m.content == '2' or m.content == '3' or m.content == '4' or m.content == '5' or m.content == '0'):
                    return True
            else:
                return False
    # continous loop to allow user to page through 5 results at a time until anime found based on text search, 15 second timeout if no response
    while True:
        try:
            messagereply = await bot.wait_for('message', timeout=15, check=check)
            msgcontent = messagereply.content
            if(msgcontent == '0'):
                try:
                    anime_list = await get_anime_list(NULL, anime_list['paging']['next'])
                    animetitles = jsontitles(anime_list)
                    animeresults.set_field_at(0, name = "Anime:", value = animetitles)
                except KeyError:
                    animeresults.set_field_at(0, name = "NO MORE PAGES LEFT", value = animetitles)
                await message.edit(embed=animeresults)
            elif(msgcontent == '1' or msgcontent == '2' or msgcontent == '3' or msgcontent == '4' or msgcontent == '5'):
                animeselection = int(msgcontent) - 1
                anime_info = await get_anime_info(anime_list['data'][animeselection]['node']['id'])
                aniEmbed = anime_info_embed(anime_info)
                await message.edit(embed=aniEmbed)
                await messagereply.delete()
                break
            await messagereply.delete()
        except asyncio.TimeoutError:
            errormsg = discord.Embed(title = "Time ran out for search, please try again", colour = discord.Colour.blue())
            await message.edit(embed=errormsg)
            break

@bot.command(name="mangainfo")
async def searchmanga(ctx, *, search_query: str):
    mangaquery = search_query.replace(" ", "%20")
    manga_list = await get_manga_list(mangaquery, NULL)
    mangatitles = jsontitles(manga_list)
    mangaresults = discord.Embed(title = "Did you mean?...", colour = discord.Colour.dark_red())
    mangaresults.add_field(name = "Manga:", value = mangatitles)
    mangaresults.set_footer(text="Please type the number of your manga")

    message = await ctx.send(embed=mangaresults)

    def check(m):
            if(m.author == ctx.author):
                if(m.content == '1' or m.content == '2' or m.content == '3' or m.content == '4' or m.content == '5' or m.content == '0'):
                    return True
            else:
                return False
    # continous loop to allow user to page through 5 results at a time until manga found based on text search, 15 second timeout if no response
    while True:
        try:
            messagereply = await bot.wait_for('message', timeout=15, check=check)
            msgcontent = messagereply.content
            if(msgcontent == '0'):
                try:
                    manga_list = await get_manga_list(NULL, manga_list['paging']['next'])
                    mangatitles = jsontitles(manga_list)
                    mangaresults.set_field_at(0, name = "Manga:", value = mangatitles)
                except KeyError:
                    mangaresults.set_field_at(0, name = "NO MORE PAGES LEFT", value = mangatitles)
                await message.edit(embed=mangaresults)
            elif(msgcontent == '1' or msgcontent == '2' or msgcontent == '3' or msgcontent == '4' or msgcontent == '5'):
                mangaselection = int(msgcontent) - 1
                manga_info = await get_manga_info(manga_list['data'][mangaselection]['node']['id'])
                mangaEmbed = manga_info_embed(manga_info)
                await message.edit(embed=mangaEmbed)
                await messagereply.delete()
                break
            await messagereply.delete()
        except asyncio.TimeoutError:
            errormsg = discord.Embed(title = "Time ran out for search, please try again", colour = discord.Colour.dark_red())
            await message.edit(embed=errormsg)
            break

#start of program
if (__name__ == '__main__'):
    main()