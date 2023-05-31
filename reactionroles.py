import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)
react_channel_id = 123456789 #channel id here


@bot.event
async def on_ready():
    print(f'Bot is ready and logged in as {bot.user}')

# Checks reactions and adds roles
@bot.event
async def on_raw_reaction_add(payload):
    guild_id = payload.guild_id
    guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)
    if guild is None:
        return

    emoji = payload.emoji.name
    role_name = payload.emoji.name

    role = discord.utils.get(guild.roles, name=role_name)
    if role is not None:
        channel = bot.get_channel(payload.channel_id)
        member = guild.get_member(payload.user_id)
        # Check if channel isn't private, a forum, voice, or a category
        if (
            channel is not None
            and not (
                isinstance(channel, discord.ForumChannel)
                or isinstance(channel, discord.CategoryChannel)
                or isinstance(channel, discord.abc.PrivateChannel)
                or isinstance(channel, discord.VoiceChannel)
            )
            ):
            print("Channel is not a valid type")
            return
        # Check if channel exists and member is not a bot
        elif channel is not None and member is not None and not member.bot:
            if isinstance(channel, discord.TextChannel):
                message = await channel.fetch_message(payload.message_id)
                await member.add_roles(role)
                print(f"Assigned role {role_name} to user {member.display_name} for reacting with {emoji} in message {message.id}")
            else:
                print("Channel type is not fetchable")

@bot.command()
@commands.has_permissions(administrator=True)
async def reactroles(ctx, *args):
    channel = ctx.channel

    if channel is not None:
        # Check if channel isn't private, a forum, voice, or a category
        if isinstance(channel, (discord.abc.PrivateChannel, discord.CategoryChannel, discord.ForumChannel, discord.VoiceChannel)):
            await ctx.send("This is not a valid channel")
        else:
            # Do reaction role stuff
            async for message in channel.history(limit=1):

                if message.author == bot.user:
                    #handle spaces in role names
                    merged_args = []
                    for arg in args:
                        if "/" not in arg:
                            merged_args.append(" " + arg)
                        else:
                            merged_args.append(arg)

                    for mapping in merged_args:
                        emoji, role_name = mapping.split('/')
                        if role_name != 'admin':
                            await add_reaction_role(ctx, message, emoji, role_name)
                        else:
                            await ctx.send("You can't add admin role")
                            print("You can't add admin role")
                    break

# Adds reactions to message
async def add_reaction_role(ctx, message, emoji, role_name):
    try:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role is not None:
            await message.add_reaction(emoji)
            print(f"Added reaction {emoji} for role {role_name}")
        else:
            await ctx.send(f"Role '{role_name}' doesn't exist")
            print(f"Role '{role_name}' doesn't exist")
    # Error handling
    except discord.Forbidden:
        await ctx.send("I can't add reactions here")
        print("I can't add reactions")
    except discord.NotFound:
        await ctx.send("Invalid emoji")
        print("Invalid emoji")
    except Exception:
        await ctx.send("Unknown error")
        print("Unknown error")

bot.run('YOUR_BOT_TOKEN_HERE')