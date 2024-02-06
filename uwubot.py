import discord
from discord.ext import commands
from datetime import datetime, timedelta
import csv
import re
import random
import os
from couscous_process import run_couscous_update, add_one_point


# Constantes
# PROC_CHANCE = 0.25
# use for di / cri function currently disabled


# Load Token
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
        channel_id = '1159147161255161906' # Deploy
        #channel_id = '798147472873750552'  # Dev
        user_allowed = 498578445081509889   # me only
        
        if ctx.author.id == user_allowed :
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
            
            run_couscous_update(csv_file_path)
            
            await ctx.send("MAJ !")
        
        else : 
            await ctx.send("Recap pliz")


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
        
        last_modif_ts = os.path.getmtime("./results/global.csv")
        last_modif_datetime = datetime.fromtimestamp(last_modif_ts)
        
        message_content += "Dernière M.À.J : " + last_modif_datetime.strftime("%d/%m/%Y - %H:%M")
        
        await ctx.send(message_content)
      
        
    @commands.command(name="ajout", help="Ajoute des points à la main")
    async def ajout(self, ctx, 
                    user: discord.User = commands.parameter(description="Mention de l'utilisateur"),
                    category: str = commands.parameter(description="c / k / ck")):
        
        user_allowed = 498578445081509889 # me only
        
        if ctx.author.id == user_allowed :
            timestamp = ctx.message.created_at
            month = timestamp.month
            
            if category == "c" :
                cat_format = "couscous"
            elif category == "k" :
                cat_format = "kayak"
            elif category == "ck" :
                cat_format = "ck"
            else :
                cat_format = "bad"                
            
            if cat_format != "bad" :
                add_one_point(user.name, month, cat_format)
                await ctx.send("Updated !")
            else : 
                await ctx.send("Mauvaise entrée")
        else :
            await ctx.send("Not authorized")
            
            
    

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
        
    
    @commands.command(name="wannadie", help="L'image que Fanny met tout le temps quand elle est au bout de sa vie")
    async def wannadie(self, ctx):
        img_path = "./images/enviedecaner.jpg"
        with open(img_path, 'rb') as image_file:
            await ctx.send(file=discord.File(image_file, 'image.jpg'))


###########################################################################################################################################


class Ping(commands.Cog, name="Ping Commands"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="blip", help="Je suis un robot")
    async def blip(self, ctx):
        await ctx.send("```blip bloup je suis un robot```")
        

###########################################################################################################################################


#@bot.event
#async def on_message(message):
    # Ignore messages from the bot itself to avoid potential infinite loops
#    if message.author == bot.user:
 #       return

    # Use a regular expression to find the part of the word after "di" or "cri" (case-insensitive)
  #  match = re.search(r'(?:di|cri)(.*)', message.content, re.IGNORECASE)

   # if match and random.random() <= PROC_CHANCE:
        # Get the cut word and the matched prefix
    #    cut_word = match.group(1)
     #   word = match.group(0).lower()  # Get the matched word

      #  if "cri" in word:
       #     cut_word = cut_word.upper()
            
        #await message.channel.send(f'`{cut_word}`')       
 
 
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
