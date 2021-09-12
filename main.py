import discord
import aiohttp
import random
import asyncio
import time
import pymongo
import youtube_dl
import json
import os
import datetime
import re
from copy import deepcopy
from pymongo import MongoClient
from aiohttp import request
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord_slash import SlashCommand

intents = discord.Intents.default()
client = commands.Bot(command_prefix="#", intents=discord.Intents.all())
client.remove_command("help")
slash = SlashCommand(client, sync_commands=True)

players = {}


@client.event
async def on_ready():
	print("Bot is ready to be used")


@client.event
async def on_member_join(member):
	role = discord.utils.get(member.server.roles, name='Family friend')
	await client.add_roles(member, role)


@client.command()
async def swag(ctx):
	await ctx.send("**`S W A G`**")


@client.command()
async def hello(ctx):
    await ctx.send("hello")






@client.command()
async def servers(ctx):
    embed = discord.Embed(
        tittle = "Servers",
        description = f"I am on {len(client.guilds)} servers",
        color=ctx.author.colour)
    await ctx.send(embed = embed)






@client.command()
async def fact(self, ctx, animal: str):
	URL = "https://some-random-api.ml/facts/dog"

	async with request("GET", URL, headers=[]) as response:
		if response.status == 200:
			data = await response.json()

			text = ctx.send(data["fact"])

		else:
			await ctx.send(f"API returned a {response.status} status")


def convert(time):
	pos = ["s", "m", "h", "d"]

	time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

	unit = time[-1]

	if unit not in pos:
		return -1
	try:
		val = int(time[:-1])
	except:
		return -2

	return val * time_dict[unit]


@client.command()
@commands.has_permissions(kick_members=True)
async def giveaway(ctx):
	await ctx.send(
	    " let’s getting **FUCKING** started in this giveaway Answer the next questions within 15 seconds"
	)

	questions = [
	    "what channel should it be hosted in",
	    "what should the duration of the giveaway be",
	    "what is the prize of the giveaway"
	]

	answers = []

	def check(m):
		return m.author == ctx.author and m.channel == ctx.channel

	for i in questions:
		await ctx.send(i)

		try:
			msg = await ctx.wait_for('message', timeout=15.0, check=check)
		except asyncio.TimeoutError:
			await ctx.send(
			    "You didn't answer in time run the command again and be faster next time"
			)
			return
		else:
			answers.append(msg.content)

		try:
			c_id = int(answers[0][2:-1])
		except:
			await ctx.send(
			    f"You didn't mention a channel properly run the command again and mention a channel properly"
			)
			return

		channel = client.get_channel(c_id)

		time = convert(answers[1])
		if time == -1:
			await ctx.send(
			    f"You didn't answer the time with a proper unit. Use (s|m|h|d)"
			)
			return
		elif time == -2:
			await ctx.send(
			    f"The time must be an integer. enter an integer next time")
			return

		prize = answers[2]

		await ctx.send(
		    f"The giveaway will be in {channel.mention} and will last {answers[1]}"
		)

		embed = discord.Embed(title="Giveaway",
		                      description=f"{prize}",
		                      color=ctx.author.color)

		embed.add_field(name="Hosted by:", value=ctx.author.mention)

		embed.set_footer(text=f"Ends {answers[1]} from now")

		my_msg = await channel.send(embed=embed)

		await my_msg.add_reaction("💸")

		await asyncio.sleep(time)

		new_msg = await channel.fetch_message(my_msg.id)

		users = await new_msg.reactions[0].users().flatten()
		users.pop(users.index(client.user))

		winner = random.choice(users)

		await channel.send(f"Congratulations {winner.mention} won {prize}")


@client.event
async def on_member_join(member,ctx):
	welcomeEmbed = discord.Embed(title=f"{member.mention}has joined the server",
	                             colour=discord.Colour.blue())
	await client.get_channel(803068205852655667).send(embed=welcomeEmbed)


@client.command(pass_content=True)
async def join(ctx):
	channel = ctx.message.author.voice.voice_channel
	await client.join_voice_channel(channel)


@client.command()
async def play(ctx, url: str):
	song_there = os.path.isfile("song.mp3")
	try:
		if song_there:
			os.remove("song.mp3")
	except PermissionError:
		await ctx.send(
		    "Wait for the current playing music to end or use the 'stop' command"
		)
		return

	voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='Music 1')
	await voiceChannel.connect()
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

	ydl_opts = {
	    'format':
	    'bestaudio/best',
	    'postprocessors': [{
	        'key': 'FFmpegExtractAudio',
	        'preferredcodec': 'mp3',
	        'preferredquality': '192',
	    }],
	}
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		ydl.download([url])
	for file in os.listdir("./"):
		if file.endswith(".mp3"):
			os.rename(file, "song.mp3")
	voice.play(discord.FFmpegPCMAudio("song.mp3"))


@client.command()
async def leave(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	if voice.is_connected():
		await voice.disconnect()
	else:
		await ctx.send("The bot is not connected to a voice channel.")


@client.command()
async def pause(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	if voice.is_playing():
		voice.pause()
	else:
		await ctx.send("Currently no audio is playing.")


@client.command()
async def resume(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	if voice.is_paused():
		voice.resume()
	else:
		await ctx.send("The audio is not paused.")


@client.command()
async def stop(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	voice.stop()


player1 = ""
turn = ""
gameOver = True

board = []

winningConditions = [[0, 1, 1], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7],
                     [2, 5, 8], [0, 4, 8], [2, 4, 6]]

player1 = ""
turn = ""
gameOver = True

board = []

winningConditions = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7],
                     [2, 5, 8], [0, 4, 8], [2, 4, 6]]


@client.command(aliases=['ttt'])
async def tictactoe(ctx, p1: discord.Member, p2: discord.Member):
	global count
	global player1
	global player2
	global turn
	global gameOver

	if gameOver:
		global board
		board = [
		    ":white_large_square:", ":white_large_square:",
		    ":white_large_square:", ":white_large_square:",
		    ":white_large_square:", ":white_large_square:",
		    ":white_large_square:", ":white_large_square:",
		    ":white_large_square:"
		]
		turn = ""
		gameOver = False
		count = 0

		player1 = p1
		player2 = p2

		# print the board
		line = ""
		for x in range(len(board)):
			if x == 2 or x == 5 or x == 8:
				line += " " + board[x]
				await ctx.send(line)
				line = ""
			else:
				line += " " + board[x]

		# determine who goes first
		num = random.randint(1, 2)
		if num == 1:
			turn = player1
			await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
		elif num == 2:
			turn = player2
			await ctx.send("It is <@" + str(player2.id) + ">'s turn.")
	else:
		await ctx.send(
		    "A game is already in progress! Finish it before starting a new one."
		)


@client.command()
async def place(ctx, pos: int):
	global turn
	global player1
	global player2
	global board
	global count
	global gameOver

	if not gameOver:
		mark = ""
		if turn == ctx.author:
			if turn == player1:
				mark = ":regional_indicator_x:"
			elif turn == player2:
				mark = ":o2:"
			if 0 < pos < 10 and board[pos - 1] == ":white_large_square:":
				board[pos - 1] = mark
				count += 1

				# print the board
				line = ""
				for x in range(len(board)):
					if x == 2 or x == 5 or x == 8:
						line += " " + board[x]
						await ctx.send(line)
						line = ""
					else:
						line += " " + board[x]

				checkWinner(winningConditions, mark)
				print(count)
				if gameOver == True:
					await ctx.send(mark + " wins!")
				elif count >= 9:
					gameOver = True
					await ctx.send("It's a tie!")

				# switch turns
				if turn == player1:
					turn = player2
				elif turn == player2:
					turn = player1
			else:
				await ctx.send(
				    "Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile."
				)
		else:
			await ctx.send("It is not your turn.")
	else:
		await ctx.send("Please start a new game using the !tictactoe command.")


def checkWinner(winningConditions, mark):
	global gameOver
	for condition in winningConditions:
		if board[condition[0]] == mark and board[
		    condition[1]] == mark and board[condition[2]] == mark:
			gameOver = True


@tictactoe.error
async def tictactoe_error(ctx, error):
	print(error)
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("Please mention 2 players for this command.")
	elif isinstance(error, commands.BadArgument):
		await ctx.send(
		    "Please make sure to mention/ping players (ie. <@688534433879556134>)."
		)


@place.error
async def place_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("Please enter a position you would like to mark.")
	elif isinstance(error, commands.BadArgument):
		await ctx.send("Please make sure to enter an integer.")


@slash.slash(description="Invite the bot to your server")
async def invite(ctx):
	embed = discord.Embed(
	    title="Invite me here",
	    descriprion="Invite me here",
	    url=
	    "https://discord.com/oauth2/authorize?client_id=857365173962539008&permissions=2956062294&redirect_uri=https%3A%2F%2Fdiscord.events.stdlib.com%2Fdiscord%2Fauth%2F&scope=bot%20applications.commands",
	)
	msg = await ctx.send(embed=embed)


@client.command(pass_context=True)
async def invite(ctx):
	embed = discord.Embed(
	    title="Invite me here",
	    descriprion="Invite me here",
	    url=
	    "https://discord.com/oauth2/authorize?client_id=857365173962539008&permissions=2956062294&redirect_uri=https%3A%2F%2Fdiscord.events.stdlib.com%2Fdiscord%2Fauth%2F&scope=bot%20applications.commands",
	)
	msg = await ctx.send(embed=embed)


@client.command(pass_context=True)
async def something(ctx):
	embed = discord.Embed(
	    title="A random thing",
	    descriprion="A random thing",
	    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
	)
	msg = await ctx.send(embed=embed)


snipe_message_author = {}
snipe_message_content = {}


@client.event
async def on_message_delete(message):
	snipe_message_author[message.channel.id] = message.author
	snipe_message_content[message.channel.id] = message.content


@slash.slash(description="Shows you the latest deleted message")
async def snipe(ctx):
	channel = ctx.channel
	try:
		snipeEmbed = discord.Embed(
		    title=f"Sniped a message in #{channel.name}",
		    description=snipe_message_content[channel.id])
		snipeEmbed.set_footer(
		    text=f"deleted by {snipe_message_author[channel.id]}")
		await ctx.send(embed=snipeEmbed)
	except:
		await ctx.send(f"No deleted messages in {ctx.channel.mention}")







@client.command()
async def snipe(ctx):
	channel = ctx.channel
	try:
		snipeEmbed = discord.Embed(
		    title=f"Sniped a message in #{channel.name}",
		    description=snipe_message_content[channel.id])
		snipeEmbed.set_footer(
		    text=f"deleted by {snipe_message_author[channel.id]}")
		await ctx.send(embed=snipeEmbed)
	except:
		await ctx.send(f"No deleted messages in {ctx.channel.mention}")


@slash.slash(description="Shows you your Avatar")
async def av(ctx, member: discord.Member = None):
	if member == None:
		member = ctx.author

	memberAvatar = member.avatar_url

	avaEmbed = discord.Embed(title=f"{member.name}'s avatar")
	avaEmbed.set_image(url=memberAvatar)

	await ctx.send(embed=avaEmbed)


@client.command(aliases=['av'])
async def avatar(ctx, member: discord.Member = None):
	if member == None:
		member = ctx.author

	memberAvatar = member.avatar_url

	avaEmbed = discord.Embed(title=f"{member.name}'s avatar")
	avaEmbed.set_image(url=memberAvatar)

	await ctx.send(embed=avaEmbed)



@client.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.bot.logout()



@client.command(aliases=["quit"])
@commands.is_owner()
async def close(ctx):
    await client.close()


@client.command()
@commands.is_owner()
async def login(ctx):
    await ctx.bot.login()



@client.command()
async def cat(ctx):
	await ctx.send(
	    "https://images-ext-1.discordapp.net/external/skqaqx8nLOMQHVB0TJxR4z3fzufrTNeMPOoN23IDwDM/https/c.tenor.com/evoSxqcmKCYAAAAM/soviet-cat-sovicat.gif"
	)


@client.command()
async def mlgfrog(ctx):
	await ctx.send(
	    "https://images-ext-1.discordapp.net/external/e9c5Jw50bAEIT8S86d-UnvTGDGUnfi8VZfRqgtCH8HE/https/c.tenor.com/QuiI1_p0YPgAAAAd/miksi0100.gif?width=500&height=375"
	)


@client.command()
async def userinfo(ctx, member: discord.Member = None):
	member = ctx.author if not member else member
	roles = [role for role in member.roles]

	embed = discord.Embed(colour=member.color,
	                      timestamp=ctx.message.created_at)

	embed.set_author(name=f"User info - {member}")
	embed.set_thumbnail(url=member.avatar_url)

	embed.add_field(name="ID", value=member.id)
	embed.add_field(name="Guild name:", value=member.display_name)

	embed.add_field(
	    name="Created at:",
	    value=member.created_at.strftime("%a, %#d %D %Y, %I:%M %p PST"))
	embed.add_field(
	    name="Joined at:",
	    value=member.joined_at.strftime("%a, %#d %D %Y, %I:%M %p PST"))

	embed.add_field(name=f"Roles {len(roles)}",
	                value=" ".join([role.mention for role in roles]))
	embed.add_field(name="Top role:", value=member.top_role.mention)

	embed.add_field(name="Bot?", value=member.bot)

	await ctx.send(embed=embed)


@slash.slash(description="Shows you a users info or your info")
async def userinfo(ctx, member: discord.Member = None):
	member = ctx.author if not member else member
	roles = [role for role in member.roles]

	embed = discord.Embed(colour=member.color,
	                      timestamp=ctx.message.created_at)

	embed.set_author(name=f"User info - {member}")
	embed.set_thumbnail(url=ctx.guild.icon_url)

	embed.add_field(name="ID", value=member.id)
	embed.add_field(name="Guild name:", value=member.display_name)

	embed.add_field(
	    name="Created at:",
	    value=member.created_at.strftime("%a, %#d %D %Y, %I:%M %p PST"))
	embed.add_field(
	    name="Joined at:",
	    value=member.joined_at.strftime("%a, %#d %D %Y, %I:%M %p PST"))

	embed.add_field(name=f"Roles {len(roles)}",
	                value=" ".join([role.mention for role in roles]))
	embed.add_field(name="Top role:", value=member.top_role.mention)

	embed.add_field(name="Bot?", value=member.bot)

	await ctx.send(embed=embed)


@client.command()
async def serverinfo(ctx):
	role_count = len(ctx.guild.roles)
	list_of_bots = [bot.mention for bot in ctx.guild.members if bot.bot]

	serverinfoEmbed = discord.Embed(timestamp=ctx.message.created_at,
	                                color=ctx.author.color)
	serverinfoEmbed.set_thumbnail(url=ctx.guild.icon_url)
	serverinfoEmbed.add_field(name='Name',
	                          value=f"{ctx.guild.name}",
	                          inline=False)
	serverinfoEmbed.add_field(name='Server id',
	                          value=f"{ctx.guild.id}",
	                          inline=False)
	serverinfoEmbed.add_field(name='Member Count',
	                          value=ctx.guild.member_count,
	                          inline=False)
	serverinfoEmbed.add_field(name='Verification Level',
	                          value=str(ctx.guild.verification_level),
	                          inline=False)
	serverinfoEmbed.add_field(name='Highest Role',
	                          value=ctx.guild.roles[-2],
	                          inline=False)
	serverinfoEmbed.add_field(name='Number of Roles',
	                          value=str(role_count),
	                          inline=False)
	serverinfoEmbed.add_field(name='Bots',
	                          value=','.join(list_of_bots),
	                          inline=False)

	await ctx.send(embed=serverinfoEmbed)


@client.command()
async def poll(ctx, *, message):
	emb = discord.Embed(tittle="Poll", description=f"{message}")
	msg = await ctx.channel.send(embed=emb)
	await msg.add_reaction('👍')
	await msg.add_reaction('👎')








@client.command(description="Mutes the specified user.")
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None, pass_context=True):
	channel = client.get_channel(879453121489805352)
	guild = ctx.guild
	mutedRole = discord.utils.get(guild.roles, name="Muted")

	if not mutedRole:
		mutedRole = await guild.create_role(name="Muted")

		for channel in guild.channels:
			await channel.set_permissions(mutedRole,
			                              speak=False,
			                              send_messages=False,
			                              read_message_history=True,
			                              read_messages=False)
	embed = discord.Embed(title="muted",
	                      description=f"{member.mention} was muted ",
	                      colour=discord.Colour.light_gray())
	embed.add_field(name="reason:", value=reason, inline=False)
	await ctx.send(embed=embed)
	await member.add_roles(mutedRole, reason=reason)


@client.command(description="Unmutes a specified user.")
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member, pass_context=True):
	channel = client.get_channel(879453121489805352)
	mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

	await member.remove_roles(mutedRole)
	embed = discord.Embed(title="unmute",
	                      description=f" unmuted-{member.mention}",
	                      colour=discord.Colour.red())
	await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(manage_roles=True)
async def warn(ctx, member: discord.Member, *, reason=None, pass_context=True):
	channel = client.get_channel(821050237191323710)
	reason = reason
	embed = discord.Embed(
	    title=f"Warn",
	    description=f"Member has been warned{ctx.author.mention}",
	    color=discord.Color.red())
	embed.add_field(name="Who got warned:", value=f"{member.mention}")
	embed.add_field(name="Reason:", value=f"{reason}")

	await channel.send(embed=embed)





@client.command(aliases=['c', 'purge'])
@commands.has_permissions(kick_members=True)
async def clear(ctx, amount=5):
	await ctx.channel.purge(limit=amount)


@slash.slash(description="Shows you the bots ping")
async def ping(ctx):
	em = discord.Embed(
	    tiitle="Ping",
	    description=
	    f"<:catping:878013310681907270> My ping is {round(client.latency * 100)}ms"
	)


@client.command()
async def ping(ctx):
	em = discord.Embed(
	    title="Ping",
	    description=
	    f"<:catping:878013310681907270> My ping is {round(client.latency * 100)}ms",
	    colour=ctx.author.color)
	await ctx.send(embed=em)


@client.command(aliases=['k'])
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No Reason provieded"):
	await ctx.send(member.mention + " has been kicked")
	await member.kick(reason=reason)


@kick.error
async def kick_error(ctx, error):
	print(error)
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(
		    " **Error**  you're missing the `**kick_members**` permission")
	elif isinstance(error, commands.BadArgument):
		await ctx.send(" make sure to mention/ping a member")


@client.command(aliases=['b'])
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
	await ctx.send(member.mention + " has been banned")
	await member.ban(reason=reason)


@ban.error
async def ban_error(ctx, error):
	print(error)
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(
		    " **Error**  you're missing the `**ban_members**` permission")
	elif isinstance(error, commands.BadArgument):
		await ctx.send(" make sure to mention/ping a member")


@client.command(aliases=['ub'])
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
	banned_users = await ctx.guild.bans()
	member_name, member_disc = member.split('#')

	for banned_entry in banned_users:
		user = banned_entry.user

		if (user.name, user.discriminator) == (member_name, member_disc):
			await ctx.guild.unban(user)
			await ctx.send(member_name + " has been unbanned")
			return
	await ctx.send(member + " was not found")


@unban.error
async def unban_error(ctx, error):
	print(error)
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(
		    " **Error**  you're missing the `**ban_members**` permission")
	elif isinstance(error, commands.BadArgument):
		await ctx.send(" make sure to mention/ping a member")


class Images(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def cat(self, ctx):
		async with ctx.channel.typing():
			async with aiohttp.ClientSession() as cs:
				async with cs.get("https://aws.random.cat/meow") as r:
					data = await r.json()

					embed = discord.Embed(title="Cat")
					embed.set_image(url=data['file'])
					embed.set_footer(text="https://random.catt/")

					await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(ban_members=True)
async def lock(ctx):
	await ctx.channel.set_permissions(ctx.guild.default_role,
	                                  send_messages=False)
	await ctx.send(ctx.channel.mention + " is now locked")


@lock.error
async def mute_error(ctx, error):
	print(error)
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(
		    f" **Error**  you're missing the `**ban_members**` permission to run this command"
		)
	elif isinstance(error, commands.BadArgument):
		await ctx.send(" make sure to mention/ping a member")


@client.command()
@commands.has_permissions(ban_members=True)
async def unlock(ctx):
	await ctx.channel.set_permissions(ctx.guild.default_role,
	                                  send_messages=True)
	await ctx.send(ctx.channel.mention + " has been unlocked")


@unlock.error
async def unmute_error(ctx, error):
	print(error)
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(
		    f" **Error**  you're missing the `**ban_members**` permission to run this command"
		)
	elif isinstance(error, commands.BadArgument):
		await ctx.send(" make sure to mention/ping a member")


@slash.slash(description="Help command ")
async def help(ctx):
	em = discord.Embed(
	    title="Help, dm Amado Carrillo#5096 if you have problems with the bot")
	description = ("#help <command> for more info on the command")

	em.add_field(
	    name="Moderation",
	    value=
	    "Kick , ban , unban , mute , unmute , clear , warn(working on the command) , lock , unlock"
	)

	em.add_field(name="Invite", value="Invite")

	em.add_field(name="Something random", value="Something")

	em.add_field(name="Ping", value="The bots ping")
	em.add_field(name="Snipe", value="Snipe")

	em.add_field(name="Server Info", value="Server info")

	em.add_field(name="Avatar", value="Avatar")

	em.add_field(name="Tic tac toe", value="Tic tac toe game")

	await ctx.send(embed=em)


@client.group(invoke_without_command=True)
async def help(ctx):
	em = discord.Embed(
	    title="Help, dm Amado Carrillo#5096 if you have problems with the bot")
	description = ("#help <command> for more info on the command")

	em.add_field(
	    name="Moderation",
	    value=
	    "Kick , ban , unban , mute , unmute , clear/purge , warn , lock , unlock"
	)

	em.add_field(name="Invite", value="Invite")

	em.add_field(name="Something random", value="Something")

	em.add_field(name="Ping", value="The bots ping")
	em.add_field(name="Snipe", value="Snipe")

	em.add_field(name="Server Info", value="Server info")

	em.add_field(name="Avatar", value="Avatar")

	em.add_field(name="Tic tac toe", value="Tic tac toe game")

	await ctx.send(embed=em)


@help.command()
async def tictactoe(ctx):
	em = discord.Embed(title="Tic tac toe",
	                   description="A tic tac toe game",
	                   colour=ctx.author.color)
	em.add_field(name="**Syntax**",
	             value="#tictactoe <member/you> and <another member>")
	await ctx.send(embed=em)


@help.command()
async def kick(ctx):
	em = discord.Embed(title="Kick",
	                   description="Kicks a member from the server",
	                   colour=ctx.author.color)

	em.add_field(name="**Syntax**", value="#kick <member> [reason]")
	await ctx.send(embed=em)


@help.command()
async def ban(ctx):
	em = discord.Embed(title="Ban",
	                   description="Bans a member from the server",
	                   colour=ctx.author.color)

	em.add_field(name="**Syntax**", value="#ban <member> [reason]")
	await ctx.send(embed=em)


@help.command()
async def unban(ctx):
	em = discord.Embed(title="Unban",
	                   description="Unbans a member from the server",
	                   colour=ctx.author.color)

	em.add_field(name="**Syntax**", value="#unban <members full username>")
	await ctx.send(embed=em)


@help.command()
async def lock(ctx):
	em = discord.Embed(title="Lock",
	                   description="Locks a channel",
	                   colour=ctx.author.color)

	em.add_field(name="**Syntax**", value="#lock")
	await ctx.send(embed=em)


@help.command()
async def unlock(ctx):
	em = discord.Embed(title="Unlock",
	                   description="Unlocks a channel",
	                   colour=ctx.author.color)
	em.add_field(name="**Syntax**", value="#unlock")
	await ctx.send(embed=em)


@help.command()
async def mute(ctx):
	em = discord.Embed(title="Mute",
	                   description="Mutes a member",
	                   colour=ctx.author.color)

	em.add_field(name="**Syntax**", value="#mute <member> [reason]")
	await ctx.send(embed=em)


@help.command()
async def invite(ctx):
	em = discord.Embed(title="Invite", colour=ctx.author.color)

	em.add_field(name="Invite", value="#Invite")
	await ctx.send(embed=em)


@help.command()
async def unmute(ctx):
	em = discord.Embed(title="unmute",
	                   description="unmutes a member",
	                   colour=ctx.author.color)

	em.add_field(name="**Syntax**", value="#unmute <member>")
	await ctx.send(embed=em)


@help.command()
async def clear(ctx):
	em = discord.Embed(title="Clear/purge",
	                   description="Clears messages",
	                   colour=ctx.author.color)

	em.add_field(name="**Syntax**",
	             value="#clear <amount> or #purge <amount> ")
	await ctx.send(embed=em)


@help.command()
async def something(ctx):
	em = discord.Embed(title="Something",
	                   description="Shows you a random thing",
	                   colour=ctx.author.color)

	em.add_field(name="Something", value="#something")
	await ctx.send(embed=em)


@help.command()
async def snipe(ctx):
	em = discord.Embed(
	    title="Snipe",
	    description=
	    "Snipes a message that was deleted in the channel that you're in",
	    colour=ctx.author.color)
	em = discord.Embed(name="**Syntax**", value="#snipe")

	await ctx.send(embed=em)


@help.command()
async def serverinfo(ctx):
	em = discord.Embed(title="Server info",
	                   description="Shows you the server info",
	                   colour=ctx.author.color)

	em.add_field(name="**Syntax**", value="#serverinfo")
	await ctx.send(embed=em)


@help.command()
async def avatar(ctx):
	em = discord.Embed(title="Avatar",
	                   description="Shows you your avatar",
	                   colour=ctx.author.color)

	em.add_field(name="**Syntax**", value="#avatar")
	await ctx.send(embed=em)


@client.event
async def on_ready():
	await client.change_presence(activity=discord.Game(
	    name=f"#help on {len(client.guilds)} server"))


async def ch_pr():
	await client.wait_until_ready()

	statuses = [
	    "discord.py", f"#help on {len(client.guilds)} servers",
	    "https://www.youtube.com/watch?v=iik25wqIuFo",
	    "if you have any problems dm leafy2.0#3090"
	]

	while not client.is_closed():
		status = random.choice(statuses)

		await client.change_presence(activity=discord.Game(name=status))

		await asyncio.sleep(7)


client.loop.create_task(ch_pr())

client.run("ODU3MzY1MTczOTYyNTM5MDA4.YNOhig.zn_pvgUZrfH1A-OQr0S1c-Z_MUg")
