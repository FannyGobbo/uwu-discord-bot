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




###########################################################################################################################################

 
class Couscous(commands.Cog, name="Couscous"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="count", help="Laissez Fanny faire siouplé")
    async def count(self,
                    ctx, 
                    dd: int = commands.parameter(description="Jour"), 
                    MM: int = commands.parameter(description="Mois"), 
                    yyyy: int = commands.parameter(description="Année"), 
                    hh: int = commands.parameter(description="Heure"), 
                    mm: int = commands.parameter(description="Minutes")):
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


    @commands.command(name="recap", help="Récap des scores")
    async def recap(self, ctx):
        parsed_results = parse_csv_file("./results/global.csv")
        parsed_sorted = dict(sorted(parsed_results.items(), key=lambda item: item[1]['Total'], reverse=True))
        
        user_l = "User"
        filler = "-"
        
        message_content = "# Scores\n"
        message_content += "```"+user_l.ljust(18, " ")+"| Couscous | Kayak | Combo | Total\n"
        message_content+= filler.ljust(52, "-") + "\n"
        
        for user in parsed_sorted:
            message_content += user.ljust(18, " ") +"| " + str(parsed_sorted[user]["couscous"]).ljust(8, " ")+" | " +str(parsed_sorted[user]["kayak"]).ljust(5, " ") +" | " +str(parsed_sorted[user]["ck"]).ljust(5, " ") +" | " +str(parsed_sorted[user]["Total"]) +"\n"
        
        message_content += "```"
        await ctx.send(message_content)
    

###########################################################################################################################################
    
    
class Custom(commands.Cog, name="Custom Commands"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="repond", help="Répond wesh !")
    async def repond(
        self,
        ctx, 
        user : discord.User = commands.parameter(description="Mention de l'utilisateur")):
        for i in range(5):
            await ctx.send("wesh " + user.mention + " réponds !!!!!!")
            
    @commands.command(name="menace", help="This is a menace !")
    async def menace(
        self,
        ctx,
        user : discord.User = commands.parameter(description="Mention de l'utilisateur"),
        *, msg : str = commands.parameter(description="Message de menace")):

        await ctx.message.delete()
        await ctx.send(user.mention + " " + msg + " sinon conséquences...")


###########################################################################################################################################


class Ping(commands.Cog, name="Ping Commands"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="blip", help="Je suis un robot")
    async def blip(self, ctx):
        await ctx.send("```blip bloup je suis un robot```")
        

###########################################################################################################################################

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.CustomActivity(name="!help"))
    await bot.add_cog(Couscous(bot))
    await bot.add_cog(Custom(bot))
    await bot.add_cog(Ping(bot))


# Run the bot with the token
bot.run(TOKEN)
