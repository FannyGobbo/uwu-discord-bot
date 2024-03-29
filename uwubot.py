import discord
from discord.ext import commands
from datetime import datetime, timedelta
import csv
import re
import random
import os
from couscous_process import run_couscous_update, add_one_point, add_n_points, add_user_to_game, update_time_diff


# Constantes
ADMIN_ID = 498578445081509889
# PROC_CHANCE = 0.25
# use for di / cri function currently disabled


# month map
month_map = {
    "janvier": 1,
    "fevrier": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "aout": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "decembre": 12
}


# Load Token
with open("token", "r") as token_file:
    TOKEN = token_file.read().strip()

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)


########################################################################################################################################### USEFUL FUNCTIONS

def parse_global_csv_file(file_path):
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


# /!\ month must be int
def parse_partial_csv_file(file_path, month):
    user_count = {}
    
    with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')
        
        for row in reader:
            user = row['User']
            counts = int(row[str(month)])
            user_count[user] = counts
        
    return user_count


def full_recap ():
        parsed_results = parse_global_csv_file("./results/global.csv")
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
        
        return message_content


def month_recap (month:int):
        parsed_couscous = parse_partial_csv_file("./results/global-couscous.csv", month)
        parsed_kayak = parse_partial_csv_file("./results/global-kayak.csv", month)
        parsed_ck = parse_partial_csv_file("./results/global-ck.csv", month)
        
        user_values = {}
        for user in parsed_couscous:
            couscous_value = parsed_couscous.get(user, 0)
            kayak_value = parsed_kayak.get(user, 0)
            ck_value = parsed_ck.get(user, 0)
            total_value = couscous_value + kayak_value + ck_value
            user_values[user] = (couscous_value, kayak_value, ck_value, total_value)

        sorted_results = dict(sorted(user_values.items(), key=lambda item: item[1][3], reverse=True))
        
        user_l = "User"
        filler = "-"
        
        message_content = "# Scores\n"
        message_content += "```"+user_l.ljust(18, " ")+"| Couscous | Kayak | Combo | Total\n"
        message_content+= filler.ljust(52, "-") + "\n"
        
        for user in sorted_results:
            message_content += user.ljust(18, " ") +"| " + str(sorted_results[user][0]).ljust(8, " ")+" | " +str(sorted_results[user][1]).ljust(5, " ") +" | " +str(sorted_results[user][2]).ljust(5, " ") +" | " +str(sorted_results[user][3]) +"\n"
        
        message_content += "```"
        
        last_modif_ts = os.path.getmtime("./results/global.csv")
        last_modif_datetime = datetime.fromtimestamp(last_modif_ts)
        
        message_content += "Dernière M.À.J : " + last_modif_datetime.strftime("%d/%m/%Y - %H:%M")
        
        return message_content




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
        
        if ctx.author.id == ADMIN_ID :
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
        


    @commands.command(name="recap", help="Récap des scores (optionnel : mention du mois)")
    async def recap(self, ctx, 
                    month:str = None):
        if month is None:
            message_content = full_recap()
        else :
            month_number = month_map.get(month.lower(), None) 
            if month_number != None :
                message_content = month_recap(month_number)
            else : 
                message_content = "Ecris correctement le mois débilus !"
        
        await ctx.send(message_content)
      
        
    @commands.command(name="ajout", help="Ajoute des points à la main")
    async def ajout(self, ctx, 
                    user: discord.User = commands.parameter(description="Mention de l'utilisateur"),
                    category: str = commands.parameter(description="c / k / ck")):
        
        if ctx.author.id == ADMIN_ID :
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
       
    @commands.command(name="ajoutN", help="Ajoute plusieurs points à la main")   
    async def ajoutN (self, ctx, 
                      user: discord.User = commands.parameter(description="Mention de l'utilisateur"),
                      category: str = commands.parameter(description="c / k / ck"),
                      amount: int = commands.parameter(description="Nombre à ajouter")):
        
        if ctx.author.id == ADMIN_ID :
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
                add_n_points(user.name, month, cat_format, amount)
                await ctx.send("Updated !")
            else : 
                await ctx.send("Mauvaise entrée")
        else :
            await ctx.send("Not authorized")
            
            
    @commands.command(name='newTZ', help="update la timezone d'un utilisateur")
    async def newTZ(self, ctx,
                    user: discord.User = commands.parameter(description="Mention de l'utilisateur"), 
                    tz : int = commands.parameter(description="différence entre discord et la timezone")):
        timezone = (tz + 24) % 24 # put it positive
        
        update_time_diff(user.name, timezone)
        
        await ctx.send("Modifié !")
        
    @commands.command(name='addUser', help="here comes a new challenger")
    async def addUser(self, ctx, 
                      user : discord.User = commands.parameter(description="Mention de l'utilisateur")):
        add_user_to_game(user)
        
        await ctx.send("Ajouté !")
        
            
            
    

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
        rand = random.random()
        if rand < 0.5:
            img_path = "./images/enviedecaner.jpg"
        else:
            img_path = "./images/wannadie.jpg"

        with open(img_path, 'rb') as image_file:
            await ctx.send(file=discord.File(image_file, 'image.jpg'))
            
    @commands.command(name="mb", help="MENTAL BREAKDANCE (pliz send help)")
    async def mb(self, ctx):
        rand = random.random()
        if rand < 0.5:
            img_path = "./images/mental-breakdance.gif"
        else:
            img_path = "./images/mental-breakdance2.gif"

        with open(img_path, 'rb') as image_file:
            await ctx.send(file=discord.File(image_file, 'meantal-breakdance.gif'))


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
