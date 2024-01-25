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


def parse_csv_file(file_path):
    user_counts = {}
    
    with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')
        
        for row in reader:
            user = row['User']
            counts = {
                'couscous': int(row['couscous']),
                'kayak': int(row['kayak']),
                'ck': int(row['ck']),
                'Total': int(row['Total'])
            }
            
            user_counts[user] = counts

    return user_counts


@bot.command()
async def recap(ctx):
    parsed_results = parse_csv_file("./results/global.csv")
    parsed_sorted = dict(sorted(parsed_results.items(), key=lambda item: item[1]['Total'], reverse=True))
    
    user_l = "User"
    filler = "-"
    
    message_content = "# Scores\n"
    message_content += "```"+user_l.ljust(16, " ")+"| Couscous | Kayak | Combo | Total\n"
    message_content+= filler.ljust(50, "-") + "\n"
    
    for user in parsed_sorted:
        message_content += user.ljust(16, " ") +"| " + str(parsed_sorted[user]["couscous"]).ljust(8, " ")+" | " +str(parsed_sorted[user]["kayak"]).ljust(5, " ") +" | " +str(parsed_sorted[user]["ck"]).ljust(5, " ") +" | " +str(parsed_sorted[user]["Total"]) +"\n"
    
    message_content += "```"
    await ctx.send(message_content)
    

@bot.command()
async def repond(ctx, user):
    for i in range(5):
        await ctx.send("wesh " + user + " réponds !!!!!!")



@bot.command()
async def blip(ctx):
    await ctx.send("```blip bloup je suis un robot```")
    

@bot.command()
async def help(ctx):
    message_content = "# Commandes :\n"
    message_content = "```" # open code quote
    message_content = "!repond @user         - spam l'user tag pour qu'iel réponde\n"
    message_content = "!blip                 - je suis un robot\n"
    message_content = "!recap                - récap des scores du couscous"
    message_content = "```" # close code quote
    await ctx.send(message_content)


# Run the bot with the token
bot.run(TOKEN)
