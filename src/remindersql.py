import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
PASSWORD = os.getenv('MYSQL_PASSWORD')

cnx = mysql.connector.connect(user='root', password=PASSWORD, database='anibotdb')

# get's entire anime_table, used to check all anime broadcast times every 6 hours
def get_anime_table():
    db = cnx.cursor()
    db.execute("SELECT * FROM anime_table;")
    result = db.fetchall()
    db.close()
    return result

# get's specific anime title from anime_table
def get_anime_table_title(animeID: int):
    db = cnx.cursor()
    db.execute(f"SELECT * FROM anime_table WHERE ani_ID = {animeID};")
    result = db.fetchall()
    db.close()
    return result

# get's all users from user_table with specific ani_ID
def get_user_table(animeID: int):
    db = cnx.cursor()
    db.execute(f"SELECT * FROM user_table WHERE ani_ID = {animeID};")
    result = db.fetchall()
    db.close()
    return result


# get's all anime reminders set for specific user from user_table
def get_user_table_anime(userID: int):
    db = cnx.cursor()
    db.execute(f"SELECT * FROM user_table WHERE user_ID = {userID};")
    result = db.fetchall()
    db.close()
    return result

# Checks if anime is currently in table, id = myanimelist anime ID
def anime_table_check(animeID: int):
    db = cnx.cursor()
    db.execute(f"SELECT * FROM anime_table WHERE ani_ID = {animeID};")
    result = db.fetchall()
    db.close()
    return len(result)

# Checks if user is already in table for specific anime reminder
def user_table_check(userID: int, animeID: int):
    db = cnx.cursor()
    db.execute(f"SELECT * FROM user_table WHERE user_ID = {userID} AND ani_ID = {animeID};")
    result = db.fetchall()
    db.close()
    return len(result)

# adds anime id and info to anime_table
def anime_table_add(ani_ID: int, ani_title: str, ani_dayoftheweek: str, ani_time: str):
    try:
        db = cnx.cursor()
        db.execute(f"""INSERT INTO anime_table(ani_ID, ani_title, ani_dayoftheweek, ani_time)
                    VALUES({ani_ID}, "{ani_title}", "{ani_dayoftheweek}", "{ani_time}");""")
        cnx.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        db.close()

# adds user id and info to user_table
def user_table_add(userID: int, animeID: int):
    try:
        db = cnx.cursor()
        db.execute(f"""INSERT INTO user_table(user_ID, ani_ID)
                    VALUES({userID}, {animeID});""")
        cnx.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        db.close()


#deletes entry in anime_table
def anime_table_delete(animeID: int):
    try:
        db = cnx.cursor()
        db.execute(f"""DELETE FROM anime_table WHERE ani_ID = {animeID}
        DELETE FROM user_table WHERE ani_ID = {animeID};""")
        cnx.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        db.close()

#deletes entry in anime_table
def user_table_delete(userID: int, animeID: int):
    try:
        db = cnx.cursor()
        db.execute(f"""DELETE FROM user_table WHERE user_ID = {userID} AND ani_ID = {animeID};""")
        cnx.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        db.close()


if (__name__ == '__main__'):
    db = cnx.cursor()
    db.execute("""SELECT * FROM user_table;""")
    result = db.fetchall()
    print(result)
    #cnx.commit()
    db.close()
    