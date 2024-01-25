# UwU bot project
by Fanny Gobbo

## Requirements : 
> $ pip install discord


## Host bot : 
> $ python3.10 uwubot.py

Note that I use version 3.10 but use your version on python instead


## Discord Commands : 
> !help \<command>(optionnal)

Print all the commands available or the description of the specified commmand

<hr>

> !count dd MM yyyy hh mm

Gives the historic of messages from Spam channel from the day and time in arguments. This will be saved into a file locally.

Note the process of the file is not automatic.

<hr>

> !recap

Print the score table in the desired channel

<hr>

> !repond @user

Ping the user to ask them to answer 
Note `@user` is to replace with the tag of the user you want

<hr>

> !blip

Je suis un robot

## Process calculations :
After running the command `!count dd MM yyyy hh mm` in the discord server : 
> $ python3.10 couscous-process.py messages-list/\<your-file.csv>

Note that I use version 3.10 but use your version on python instead

## Reset calculation files :
> $ cp templates_for_reset/* results/

