import discord
import os
import asyncio
import config
from discord.ext import commands

from os import listdir
from os.path import isfile, join


bot = commands.Bot(command_prefix=str(config.prefix))
cogs_dir = "plugins"

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)

@bot.command()
async def load(extension_name : str):
    """Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))

@bot.command()
async def unload(extension_name : str):
    """Unloads an extension."""
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))

'''
@bot.event
async def on_command_error(error, ctx):
	if isinstance(error, commands.CommandNotFound):
		pass
	elif isinstance(error, commands.MissingRequiredArgument):
		await send_cmd_help(ctx)
	elif isinstance(error, commands.BadArgument):
		await send_cmd_help(ctx)
'''
async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)

if __name__ == "__main__":
	for extension in [f for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
		try:
			if str(extension)[-3:] == ".py":
				bot.load_extension(cogs_dir + "." + extension[:-3])
		except Exception as e:
			print(f'Failed to load extension {extension}.')
			traceback.print_exc()

	bot.run(config.discordtoken)

