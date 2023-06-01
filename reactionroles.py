import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents, help_command=commands.DefaultHelpCommand())


@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    print(f'Bot is ready and logged in as {bot.user}')


@bot.event
async def on_raw_reaction_add(payload):
    """Event triggered when a reaction is added to a message."""
    guild_id = payload.guild_id
    guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)
    if guild is None:
        return

    emoji_name = payload.emoji.name
    role_name = payload.role.name

    role = discord.utils.get(guild.roles, name=role_name)
    if role is not None:
        channel = bot.get_channel(payload.channel_id)
        member = guild.get_member(payload.user_id)

        if (
            channel is not None
            and member is not None
            and not member.bot
            and not isinstance(channel, (discord.ForumChannel, discord.CategoryChannel, discord.abc.PrivateChannel))
        ):
            if isinstance(channel, discord.TextChannel):
                message = await channel.fetch_message(payload.message_id)
                await member.add_roles(role)
                print(f"Assigned role {role_name} to user {member.display_name} for reacting with {emoji_name} in message {message.id}")
            else:
                print("Channel type is not fetchable")


@bot.command(brief="Assign roles based on reactions to a message.", description="Assign roles to users based on their reactions to a message.")
@commands.has_permissions(administrator=True)
async def reactroles(ctx, *args):
    """Assign roles based on reactions to a message.

    Arguments:
    - args: Pairs of emoji and role name, separated by a forward slash (/).
    """
    channel = ctx.channel
    replied_message = ctx.message.reference.resolved if ctx.message.reference else None

    if replied_message:
        merged_args = handle_map_spaces(args)
        for mapping in merged_args:
            emoji_name, role_name = mapping.split('/')
            if role_name != 'admin':
                await add_reaction_role(ctx, replied_message, emoji_name, role_name)
            else:
                await ctx.send("You can't add the admin role")
                print("You can't add the admin role")
    else:
        await ctx.send("Please reply to a message to use this command.")


async def add_reaction_role(ctx, message, emoji_name, role_name):
    """Add a reaction and assign a role to a message.

    Arguments:
    - ctx: The context of the command.
    - message: The message to add the reaction and assign the role.
    - emoji_name: The name of the emoji to react with.
    - role_name: The name of the role to assign.
    """
    try:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role is not None:
            emoji = discord.utils.get(bot.emojis, name=emoji_name)
            if emoji is not None:
                await message.add_reaction(emoji)
                print(f"Added reaction {emoji} for role {role_name}")
            else:
                await ctx.send(f"Emoji '{emoji_name}' not found")
                print(f"Emoji '{emoji_name}' not found")
        else:
            await ctx.send(f"Role '{role_name}' doesn't exist")
            print(f"Role '{role_name}' doesn't exist")
    except discord.Forbidden:
        await ctx.send("I can't add reactions here")
        print("I can't add reactions")
    except discord.NotFound:
        await ctx.send("Invalid emoji")
        print("Invalid emoji")
    except Exception:
        await ctx.send("Unknown error")
        print("Unknown error")


def handle_map_spaces(args):
    """Handle spaces in mapping arguments.

    Arguments:
    - args: List of mapping arguments.

    Returns:
    - List of merged mapping arguments.
    """
    merged_args = []
    for arg in args:
        if "/" not in arg:
            merged_args[-1] += " " + arg
        else:
            merged_args.append(arg)
    return merged_args


def read_token():
    """Read the bot token from a file named 'react_token.txt'."""
    with open("react_token.txt", "r") as file:
        token = file.read().strip()
    return token


@bot.event
async def on_command_error(ctx, error):
    """Event triggered when a command encounters an error."""
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You don't have the necessary permissions to use this command.")
    else:
        await ctx.send("An error occurred while processing the command.")


bot_token = read_token()
bot.run(bot_token)
