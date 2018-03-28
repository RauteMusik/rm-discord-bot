import discord
from discord.ext import commands
import time
import config
import asyncio
from discord import opus
import sys
import datetime
import os
import hashlib
import requests
import json
import base64

voice = None
player = None
selectedStation = "http://main-high.rautemusik.fm"
allStations = {}

class playRadio:

	def getData(self):

		print("Requesting new data from api")
		hashGen = hashlib.sha1()

		clientID = str(base64.b64decode(config.clientID).decode('UTF8')).strip()
		secretKey = str(base64.b64decode(config.secretKey).decode('UTF8')).strip()
		timestamp = str(int(time.time()))
		unhashed = str(timestamp)+str(clientID)+''+'/streams/'+str(secretKey)
		hashGen.update(unhashed.encode('utf-8'))
		hashKey = str(hashGen.hexdigest())[:12]

		headers = {'x-client-id': clientID,'x-timestamp': timestamp,'x-hash': hashKey}

		try:
			response = requests.get("https://api.rautemusik.fm/streams/",headers=headers)

			print("Got response")

			return str(response.text)

		except:
			return False

	def saveData(self,data):
		with open('result.json', 'w') as f:
			f.write(data)

	def readDataAge(self):
		fileTime = 0
		try:
			fileTime = int(datetime.datetime.utcfromtimestamp(os.path.getmtime("result.json")).timestamp())
		except:
			fileTime = 0
		now = int(time.time())
		if (int(fileTime) + 86400) < now:
			return False
		else:
			return True

	def readData(self):
		with open('result.json') as jsonfile:
			json_data = json.load(jsonfile)
		return json_data['items']
	@commands.command(pass_context=True, brief="Get available stations", name='stations')
	async def getRadioStations(self,ctx):
		global allStations
		if self.readDataAge():
			print("Data new enough")
		else:
			print("Data too old")
			data = self.getData()
			if not data is False:
				self.saveData(data)
			else:
				print("Error updating data")
		stations = self.readData()
		allStations = {}
		for station in stations:
			allStations[station['id']] = [station['tunein_urls']['mp3'],station['name']]
		embedDesc = ""
		for station in allStations:
			embedDesc = embedDesc +"\n**"+str(station) + "**: " + str(allStations[station][1])
		embed=discord.Embed(title="id: Name",description=embedDesc)
		await ctx.bot.say(embed=embed)

	@commands.command(pass_context=True, brief="Change radio station", name='change')
	async def changeRadioStation(self,ctx, station: str):
		global selectedStation
		global allStations
		if station in allStations:
			selectedStation = allStations[station][0]
			messageToSend = "Station url now "+str(selectedStation)
			print(messageToSend)
			await ctx.bot.say(messageToSend)
			try: 
				await self.startRadio.callback(self,ctx)
			except:
				pass

	@commands.command(pass_context=True, brief="Stop playing audio", name='stop')
	async def stopRadio(self,ctx):
		global player
		try:
			player.stop()
		except:
			pass
	@commands.command(pass_context=True, brief="Joins the current channel, if its a voice channel", name='join')
	async def joinChannel(self,ctx):
		global voice
		if ctx.message.author.voice_channel:
			print("SENDER IS IN VOICE")
			voice = await ctx.bot.join_voice_channel(ctx.message.author.voice_channel)
		else:
			await ctx.bot.say("You need to be in a voice channel before turning on the radio")

	@commands.command(pass_context=True, brief="Leaves the current channel, if its a voice channel", name='leave')
	async def leaveChannel(self,ctx):
		for x in ctx.bot.voice_clients:
			if(x.server == ctx.message.server):
				return await x.disconnect()

	@commands.command(pass_context=True, brief="Start playing audio", name='start')
	async def startRadio(self,ctx):
		global voice
		global player
		global selectedStation
		if not voice is None:
			print(discord.opus.is_loaded())
			try:
				player.stop()
			except:
				pass
			print("Before reading url")
			player = await voice.create_ytdl_player(selectedStation)
			print("After reading url")
			print("Before starting player")
			player.start()
			print("After starting player")

	def __init__(self,bot):
		self.bot = bot
		global allStations
		'''
		if sys.maxsize > 2**32:
			opus.load_opus('libopus-0.x64.dll')
		else:
			opus.load_opus('libopus-0.x86.dll')
		'''

		if self.readDataAge():
			print("Radio plugin: Data new enough")
		else:
			print("Radio plugin: Data too old")
			data = self.getData()
			if not data is False:
				self.saveData(data)
			else:
				print("Radio plugin: Error updating data")

		stations = self.readData()

		allStations = {}
		for station in stations:
			allStations[station['id']] = [station['tunein_urls']['mp3'],station['name']]

		print("Radio plugin started")

def setup(bot):
	bot.add_cog(playRadio(bot))
