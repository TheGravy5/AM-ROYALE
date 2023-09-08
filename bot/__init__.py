from glob import glob
from discord.ext.commands import Cog

from discord.ext.commands import Bot
import discord
import os
import time
from discord.ext import commands
from discord import Embed
from discord import Color as c
import sqlite3
from sqlite3 import Error
import codecs

# stuff needed for database

database = r"./db/amroyale.db"

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    
    return conn
 
def create_balance(conn, balance):
    """
    Create a new balance into the balance table
    :param conn:
    :param balance:
    """
    sql = ''' INSERT INTO balance(id,bal)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, balance)
    conn.commit()
    return cur.lastrowid
    
def create_data():
    
    conn = create_connection(database)
    with conn:
        balance = (ctx.author.id,'500')
        balance_id = create_balance(conn, balance)

def update_balance(conn, balance):
    """
    update bal of a balance
    :param conn:
    :param balance:
    :return: balance id
    """
    sql = ''' UPDATE balance
            SET bal = ?
            WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, balance)
    conn.commit()

# bot setup

PREFIX = "$"
OWNER_IDS = [949496206617366619]
tstart = time.time()
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# bot events

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='$ help'))

@bot.event
async def on_command(ctx):
    
    conn = create_connection(database)
    cursor=conn.cursor()
    with conn:
        cursor.execute("SELECT rowid FROM balance WHERE id = ?", (ctx.author.id,))
        exists = cursor.fetchone()
        if exists is None:
            balance = (ctx.author.id,'500')
            balance_id = create_balance(conn, balance)

# utility commands
@bot.command(brief='Gives bot connection in ms')
async def ping(ctx):
    await ctx.send(f"`{round(bot.latency * 1000)}ms`")
    
@bot.command(brief='Displays time since startup in seconds')
async def uptime(ctx):
    t = time.time()
    tdist = round(t - tstart)
    await ctx.send(f'Uptime: {tdist}s')

@bot.command(brief='Disconnects and stops the bot')
async def shutdown(ctx):
    allowed_IDs = [352178848307216384, ...]
    if ctx.author.id in allowed_IDs:
        await ctx.send("Shutting down...")
        print (f"Bot shut down by {ctx.author}")
        await bot.close()
    else:
        await ctx.send(f"No, {ctx.author.mention}.")

# currency commands

@bot.command(brief="Sets someone's balance")
async def setbal(ctx, user: discord.User, value):
    allowed_IDs = [352178848307216384, 935523589640310854, ...]
    if ctx.author.id in allowed_IDs:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        with conn:
            cursor.execute("SELECT rowid FROM balance WHERE id = ?", (user.id,))
            exists = cursor.fetchone()
            if exists is None:
                balance = (user.id,value)
                balance_id = create_balance(conn, balance)
            else:
                update_balance(conn, (value, user.id))
        embed = Embed(title="Set Balance", color=c.from_str("#00F0FF"), description=f'Balance of {user} set to {value} tokens!')
    else: 
        embed = Embed(title="Set Balance", color=c.from_str("#00F0FF"), description=f"You aren't allowed to do that, {ctx.author.mention}")
    await ctx.send(embed=embed)

@bot.command(brief="View you or someone else's balance")
async def bal(ctx, user: discord.User=None):    
    if user == None:
        user = ctx.author
    currencyType = "Tokens"
    if user.id == 931311122760474674:
        currencyType = "Snoins"
    elif user.id == 935523589640310854:
        currencyType = "ToYokens"
    elif user.id == 515739280652501002:
        currencyType = "Kidneys"
    
    conn = create_connection(database)
    """
    Query all rows in the balance table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM balance")

    rows = cur.fetchall()

    for row in rows:
        if user.id in row:
            embed = Embed(title=f"{user}'s Balance", color=c.from_str("#00F0FF"), description=f"{row[1]} {currencyType}")
            embed.set_author(name="Royale Bank", icon_url="https://cdn.discordapp.com/emojis/1148394161440047195.gif?size=40&quality=lossless")
            await ctx.send(embed=embed)

@bot.command(brief="View the leaderboard for most tokens")
async def lb(ctx, page=1):
    pagerank = ((page - 1) * 10) + 1
    pagemaxrank = pagerank + 9
    conn = sqlite3.connect(database)
    with conn:
        """
        Query balance by bal
        :param conn: the Connection object
        :return:
        """
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM balance ORDER BY bal DESC")
        rows = cursor.fetchall()
        rank = 0
        leaderboard = "There are no users on this page."
        for row in rows:
            rank = rank + 1
            isrankhigh = rank >= pagerank
            isranklow = rank <= pagemaxrank
            if isrankhigh is True and isranklow is True:
                leaderboard_value = (f"#{rank}. {row[1]} - <@{row[0]}>") 
                if rank is pagerank:
                    leaderboard = leaderboard_value
                else:
                    leaderboard = (f"{leaderboard} \n{leaderboard_value}") 

        embed = Embed(title="LEADERBOARD", color=c.from_str("#00F0FF"), description=leaderboard)
        embed.set_footer(text = f"Page {page}")
        await ctx.send(embed=embed)

@bot.command(brief="Asssign a winner to a competition")
async def award(ctx, winner: discord.User=None):
    allowed_IDs = [352178848307216384, 935523589640310854, ...]
    if ctx.author.id in allowed_IDs:
        if winner is None:
            await ctx.send("You need to mention someone to award.")
        else: 
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            
            with conn:
                cursor.execute("SELECT rowid FROM balance WHERE id = ?", (winner.id,))
                exists = cursor.fetchone()
                if exists is None:
                    balance = (winner.id,550)
                    balance_id = create_balance(conn, balance)
                else:
                    pass
                    # value = userBalance + 50
                    # update_balance(conn, (value, user.id))
            embed = Embed(title="Award", color=c.from_str("#00F0FF"), description=f"Awarded {winner}!")
    else: 
        embed = Embed(title="Award", color=c.from_str("#00F0FF"), description=f"You aren't allowed to do that, {ctx.author.mention}")
    await ctx.send(embed=embed)
@bot.command(brief='Bet some of your tokens on something')
async def bet(ctx, mode="help", target: discord.User="None", value="None"):
    if mode == "help":
        embed=Embed(title="..bet help", color=c.from_str("#00F0FF"), description=f"..bet lets you bet your tokens on something against someone else. \nWays to use this command: \nView this page \n..bet help \nBet your tokens against someone \n..bet credit [user to target] [amount to bet] \nAccept a bet \n..bet a [bet id] \nView a list of all active bets \n..bet list \nAssign a bet winner \n..bet w [bet id] [winning user]")
    else: 
        embed=Embed(title="..bet", color=c.from_str("#00F0FF"), description="Coming Soon")
    await ctx.send(embed=embed)

@bot.command(brief='Give away some tokens to someone else')
async def give(ctx):
    await ctx.send("Coming Soon")

@bot.command(brief='Spend your tokens')
async def shop(ctx):
    await ctx.send("Coming Soon")

# run bot
TOKEN = open('token.txt').read().strip()
bot.run(TOKEN)