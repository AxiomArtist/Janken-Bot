import discord
from discord.ext import commands
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="", intents=intents)

game_active = False
queue = []
game_post = None


def reset_game():
    global game_active, queue, game_post
    game_active = False
    queue = []
    game_post = None


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


async def start_countdown():
    print("Check 4: Countdown started.")
    await asyncio.sleep(300)
    if queue:
        await run_game()
    else:
        reset_game()

@bot.tree.command(name="throwdown")
async def throwdown(interaction: discord.Interaction):
    global game_active, game_post
    if game_active:
        await interaction.response.send_message("A game is already in progress. Please wait for it to finish.", ephemeral=True)
    else:
        print("Check 1: Bot activation confirmed.")
        game_active = True
        image_url = 'https://imgur.com/gallery/0tcEhrP'
        await interaction.response.send_message(image_url)
        game_post = await interaction.original_response()
        print("Check 2: Image post and instructions confirmed.")

        for emoji in ['✊', '✋', '✌️']:
            await game_post.add_reaction(emoji)
            print(f"Check 3: Bot reaction with {emoji} confirmed.")

        await start_countdown()



@bot.event
async def on_reaction_add(reaction, user):
    global queue
    if user == bot.user:
        return

    if reaction.message.id == game_post.id:
        if str(reaction.emoji) in ['✊', '✋', '✌️']:
            for i in range(len(queue)):
                if queue[i][0] == user:
                    await game_post.remove_reaction(queue[i][1], user)
                    del queue[i]
                    break
            queue.append((user, str(reaction.emoji)))
            print(f"Check 5: Player {user.name} added to the queue with move {str(reaction.emoji)}.")


async def run_game():
    global game_active, queue, game_post

    print("Check 6: Game started.")
    bot_move = random.choice(['✊', '✋', '✌️'])
    print(f"Check 7: Bot's move chosen: {bot_move}")
    rps_results = {
        ('✊', '✊'): 'Tie',
        ('✊', '✋'): 'Lose',
        ('✊', '✌️'): 'Win',
        ('✋', '✊'): 'Win',
        ('✋', '✋'): 'Tie',
        ('✋', '✌️'): 'Lose',
        ('✌️', '✊'): 'Lose',
        ('✌️', '✋'): 'Win',
        ('✌️', '✌️'): 'Tie',
    }
    results = []

    for player, player_reaction in queue:
        result = rps_results[(player_reaction, bot_move)]
        results.append((player, player_reaction, result))

    result_message = f"Bot's move: {bot_move}\n"
    for player, move, outcome in results:
        if outcome in ["Win", "Tie", "Lose"]:
            result_message += f"{player.mention} ({player.name}) chose {move} they {outcome}!\n"

    await game_post.channel.send(result_message)
    print("Check 8: Winner, Tie or Lose determined.")
    reset_game()
    print("Check 9: Game reset.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

print("Check 10: something buggered.")



bot.run("Bot Token")


