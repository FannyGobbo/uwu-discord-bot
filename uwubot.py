import discord
from discord.ext import commands
from datetime import datetime, timedelta
import csv

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
with open("token", "r") as token_file:
    TOKEN = token_file.read().strip()

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')
    

@bot.command()
async def count(ctx, dd: int, MM: int, yyyy: int, hh: int, mm: int):
    # Replace 'YOUR_CHANNEL_ID' with the actual channel ID
    channel_id = '1159147161255161906'

    # Convert the provided date and time arguments into a datetime object
    start_date = datetime(yyyy, MM, dd, hh, mm, 0)
    end_date = datetime.utcnow()

    channel = bot.get_channel(int(channel_id))

    # Fetch messages within the specified timeframe
    messages = []
    async for message in channel.history(limit=None, after=start_date, before=end_date):
        messages.append({
            'timestamp': message.created_at.strftime('%d/%m %H:%M'),
            'user': message.author.name,
            'message': message.content
        })

    # Write messages to a CSV file
    csv_file_path = f'messages-list/messages_{start_date.strftime("%Y%m%d%H%M")}_{end_date.strftime("%Y%m%d%H%M")}.csv'
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['timestamp', 'user', 'message']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # Write the header
        writer.writeheader()

        # Write messages
        writer.writerows(messages)

    print(f'Messages written to {csv_file_path}')







# Run the bot with the token
bot.run(TOKEN)
