from asyncio.windows_events import NULL
import os
import discord
from PIL import Image
import asyncio
from discord import colour
from discord.embeds import Embed, EmptyEmbed
from discord.ext.commands.errors import ExpectedClosingQuoteError
from malfunc import *
from remindersql import *
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='f^', help_command=None)

WEEKDAYS = [(0, 'monday'), (1, 'tuesday'), (2, 'wednesday'), (3, 'thursday'), (4, 'friday'), (5, 'saturday'), (6, 'sunday')]

# Main start of program, begins asyncio loop to refresh token regardless of access every set amount of time
def main():
    loop = asyncio.get_event_loop()
    loop.create_task(refreshtimer())
    loop.create_task(anime_reminders())

    print("Fukuro-Sama is online!")
    bot.run(TOKEN)

def anihourswitcher(i):
    switcher = {
        20: 0,
        21: 1,
        22: 2,
        23: 3
    }
    return switcher.get(i)

async def anime_reminders():
    while True:
        tz_japan = pytz.timezone('Japan')
        datetime_japan = datetime.now(tz_japan)
        dtj_day = datetime_japan.weekday()
        dtj_hour = int(datetime_japan.strftime("%H"))
        
        result = get_anime_table()

        for i in range(len(result)):
            ani_daystr = result[i][2]
            for k in WEEKDAYS:
                if(k[1] == ani_daystr):
                    ani_day = k[0]
            ani_hourbase = int(result[i][3][:2])
            if(ani_hourbase >= 20):
                ani_hour = anihourswitcher(ani_hourbase)
                if(ani_day <= 5):
                    extraday  = ani_day + 1
                else:
                    extraday = 0
            else:
                ani_hour = ani_hourbase + 4

            if(ani_day == dtj_day or (ani_hourbase >= 20 and extraday == dtj_day)):
                if(ani_hourbase <= dtj_hour and ani_hour > dtj_hour):
                    users = get_user_table(result[i][0])
                    if(len(users) == 0):
                        anime_table_delete(result[i][0])
                        continue
                    ani_info = await get_anime_sql_info(result[i][0])
                    remindermsg = discord.Embed(title = f"Hoot Hoot! New episode today for {result[i][1]}!", colour = discord.Colour.blue())
                    remindermsg.set_image(url=ani_info['main_picture']['large'])
                    remindermsg.set_author(name='Fukuro', icon_url='https://i.postimg.cc/RhM2kYLS/finalfukuro.png')
                    remindermsg.set_thumbnail(url='https://i.postimg.cc/RhM2kYLS/finalfukuro.png')
                    remindermsg.set_footer(text="Episode release expected today unless outlying circumstances")

                    for h in range(len(users)):
                        user = await bot.fetch_user(users[h][0])
                        await user.send(embed=remindermsg)
                    
                    if(ani_info['status'] != "currently_airing"):
                        anime_table_delete(ani_info['id'])

        await asyncio.sleep(14400)

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
    result.set_author(name='Fukuro', icon_url='https://i.postimg.cc/RhM2kYLS/finalfukuro.png')
    result.set_thumbnail(url='https://i.postimg.cc/RhM2kYLS/finalfukuro.png')
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
    result.set_author(name='Fukuro', icon_url='https://i.postimg.cc/RhM2kYLS/finalfukuro.png')
    result.set_thumbnail(url='https://i.postimg.cc/RhM2kYLS/finalfukuro.png')
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


@bot.command()
async def help(ctx):
    em = discord.Embed(title="Command List", description = "**prefix = f^**", colour = discord.Colour.dark_orange())
    em.set_thumbnail(url='https://i.postimg.cc/RhM2kYLS/finalfukuro.png')
    em.set_footer(text="Thank you for using Fukuro!")
    em.add_field(name="animeinfo", value="Search for anime information, e.g 'f^animeinfo one piece'", inline=False)
    em.add_field(name="mangainfo", value="Search for manga information, e.g 'f^mangainfo one piece'", inline=False)
    em.add_field(name="add-reminder", value="Add yourself to be reminded when an episode releases of your favorite anime, e.g 'f^add-reminder one piece'", inline=False)
    em.add_field(name="remove-reminder", value="Remove episode reminder, e.g 'f^remove-reminder'", inline=False)
    await ctx.send(embed=em)

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
                try:
                    animeselection = int(msgcontent) - 1
                    anime_info = await get_anime_info(anime_list['data'][animeselection]['node']['id'])
                    aniEmbed = anime_info_embed(anime_info)
                    await message.edit(embed=aniEmbed)
                    await messagereply.delete()
                    break
                except IndexError as e:
                    print(e)
                    continue
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
                try:
                    mangaselection = int(msgcontent) - 1
                    manga_info = await get_manga_info(manga_list['data'][mangaselection]['node']['id'])
                    mangaEmbed = manga_info_embed(manga_info)
                    await message.edit(embed=mangaEmbed)
                    await messagereply.delete()
                    break
                except IndexError as e:
                    print(e)
                    continue
            await messagereply.delete()
        except asyncio.TimeoutError:
            errormsg = discord.Embed(title = "Time ran out for search, please try again", colour = discord.Colour.dark_red())
            await message.edit(embed=errormsg)
            break


# Adds user to database of reminders, where the user will be reminded of an anime's new ep release
@bot.command(name="add-reminder")
async def add_reminder(ctx, *, search_query: str):
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
                try:
                    animeselection = int(msgcontent) - 1
                    anime_info = await get_anime_sql_info(anime_list['data'][animeselection]['node']['id'])

                    if(anime_info['status'] != "currently_airing"):
                        errormsg = discord.Embed(title = "Sorry, can only remind you of shows that are currently airing!", colour = discord.Colour.blue())
                        await message.edit(embed=errormsg)
                        await messagereply.delete()
                        break

                    user_ID = ctx.author.id

                    if(anime_table_check(anime_info['id']) == 0):
                        anime_table_add(anime_info['id'], anime_info['title'], anime_info['broadcast']['day_of_the_week'], anime_info['broadcast']['start_time'])
                        user_table_add(user_ID, anime_info['id'])
                        successmsg = discord.Embed(title = f"{anime_info['title']} episode reminder added!", colour = discord.Colour.blue())
                        successmsg.set_image(url=anime_info['main_picture']['large'])
                        successmsg.set_author(name='Fukuro', icon_url='https://i.postimg.cc/RhM2kYLS/finalfukuro.png')
                        successmsg.set_thumbnail(url='https://i.postimg.cc/RhM2kYLS/finalfukuro.png')
                        await message.edit(embed=successmsg)
                        await messagereply.delete()
                        break
                    else:
                        if(user_table_check(user_ID, anime_info['id']) == 1):
                            errormsg = discord.Embed(title = f"{anime_info['title']} episode reminder is already placed! Don't worry, we won't forget :wink:", colour = discord.Colour.blue())
                            errormsg.set_image(url=anime_info['main_picture']['large'])
                            await message.edit(embed=errormsg)
                            await messagereply.delete()
                            break
                        else:
                            user_table_add(user_ID, anime_info['id'])
                            successmsg = discord.Embed(title = f"{anime_info['title']} episode reminder added!", colour = discord.Colour.blue())
                            successmsg.set_image(url=anime_info['main_picture']['large'])
                            successmsg.set_author(name='Fukuro', icon_url='https://i.postimg.cc/RhM2kYLS/finalfukuro.png')
                            successmsg.set_thumbnail(url='https://i.postimg.cc/RhM2kYLS/finalfukuro.png')
                            await message.edit(embed=successmsg)
                            await messagereply.delete()
                            break
                except IndexError as e:
                    print(e)
                    continue
                
            await messagereply.delete()
        except asyncio.TimeoutError:
            errormsg = discord.Embed(title = "Time ran out , please try again", colour = discord.Colour.blue())
            await message.edit(embed=errormsg)
            break


# removes user from database of reminders
@bot.command(name="remove-reminder")
async def remove_reminder(ctx):

    userID = ctx.author.id

    user_animes = get_user_table_anime(userID)
    if(len(user_animes) == 0):
        errormsg = discord.Embed(title = f"You currently have 0 reminders", colour = discord.Colour.blue())
        await ctx.send(embed=errormsg)
        return
    animetitles = ""
    numofreminders = 0
    ani_titles = []
    for i in range(len(user_animes)):
        ani_title = get_anime_table_title(user_animes[i][1])
        ani_titles.append(ani_title[0][1])
        animetitles = animetitles + f"{i+1}. {ani_title[0][1]}\n"
        numofreminders += 1
    animetitles = animetitles + "\n0. Cancel removal"
    reminderresults = discord.Embed(title = "Which Reminders did you want removed?", colour = discord.Colour.blue())
    reminderresults.add_field(name = 'Reminders:', value = animetitles)
    reminderresults.set_footer(text="Please type the number of your reminder you wish to remove")
    message = await ctx.send(embed=reminderresults)

    def check(m):
            if(m.author == ctx.author):
                if(int(float(m.content)) <= numofreminders and int(float(m.content)) >= 0):
                    return True
            else:
                return False
    
    while True:
        try:
            messagereply = await bot.wait_for('message', timeout=15, check=check)
            msgcontent = int(float(messagereply.content)) - 1
            if(msgcontent == -1):
                errormsg = discord.Embed(title = f"Cancelled", colour = discord.Colour.blue())
                await message.edit(embed=errormsg)
                await messagereply.delete()
                break
            result = user_table_delete(userID, user_animes[msgcontent][1])
            if(result):
                successmsg = discord.Embed(title = f"{ani_titles[msgcontent]} episode reminder removed", colour = discord.Colour.blue())
                await message.edit(embed=successmsg)
                await messagereply.delete()
                break
            else:
                errormsg = discord.Embed(title = f"{ani_titles[msgcontent]} episode reminder was unable to be removed", colour = discord.Colour.blue())
                await message.edit(embed=errormsg)
                await messagereply.delete()
                break
        except asyncio.TimeoutError:
            errormsg = discord.Embed(title = "Time ran out, please try again", colour = discord.Colour.blue())
            await message.edit(embed=errormsg)
            break

#start of program
if (__name__ == '__main__'):
    main()