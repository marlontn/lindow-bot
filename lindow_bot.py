import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, time, timedelta
import discord
from discord import ButtonStyle, app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View
from functools import lru_cache
from random import randint, choice, sample
import requests
import sqlite3
import super_secret

guild = discord.Object(id=super_secret.guild_id)
DAILY_WORD_TIME = time(5,0,0)

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.synced = False
    
    async def on_ready(self):
        await tree.sync()
        await tree.sync(guild=guild)
        self.synced = True
        await self.change_presence(activity=discord.Game('Fighting aragami'))
        self.send_daily_word.start()
        print('Bot is online!')
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if 'lindow' in message.content.lower():
            await message.channel.send('did somebody call me :smirk:')
            return
        
        if 'code vein' in message.content.lower():
            await message.channel.send('what a good game :weary:')
            return
    
    @tasks.loop(time=DAILY_WORD_TIME)
    async def send_daily_word(self):
        channel = self.get_channel(super_secret.betterwords_id)
        url = 'https://www.merriam-webster.com/word-of-the-day'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string
        word = title.split(': ', 1)[1].split(' |', 1)[0]
        await channel.send(f'Word of the day: {word}')
        print(f'Word of the day "{word}" has been sent')

bot = MyBot()
tree = app_commands.CommandTree(bot)

@lru_cache
def search(word):
    word = ''.join(c for c in word.lower() if c.isalnum() or c in ' -\'')
    if not word: return dict()
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={super_secret.api_key}'

    r = requests.get(url)
    if r.status_code != 200:
        return {'error': 'either the request failed or the daily request limit has been reached.'}

    results = r.json()
    
    if not results:
        return {'error': f'{word.lower()} could not be found.'}
    elif type(results[0]) == str:
        return {'similar': results}

    act_word = ''
    defs = []
    for entry in results:
        e_word = entry['meta']['id'].split(':')[0]
        if e_word.lower() != word: continue
        if not act_word: act_word = e_word
        fl = entry.get('fl','')
        if not fl: continue
        for definition in entry['shortdef']:
            defs.append({'fl':fl, 'def':definition})
    
    return {'word':act_word, 'defs':defs} if defs else {'error': f'{word.lower()} could not be found.'}

@lru_cache
def search_verbose(word):
    word = ''.join(c for c in word.lower() if c.isalnum() or c == ' ')
    if not word: return dict()
    r = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')

    if r.status_code != 200:
        return {'error': f'{word.lower()} could not be found.'}
    
    results = r.json()
    act_word = ''
    defs = []
    for res in results:
        if not act_word: act_word = res.get('word','')
        for meaning in res['meanings']:
            fl = meaning['partOfSpeech']
            for definition in meaning['definitions']:
                _def = definition['definition']
                
                example = ''
                if 'example' in definition:
                    example = definition['example'].split()
                    for j in range(len(example)):
                        if word in example[j].lower():
                            example[j] = f'*{example[j]}*'
                    example = ' '.join(example)
                
                synonyms = definition.get('synonyms',[])
                antonyms = definition.get('antonyms',[])
                
                defs.append({'fl':fl, 'def':_def, 'ex':example, 'syn':synonyms, 'ant':antonyms})
    
    return {'word':act_word, 'defs':defs}

@tree.command(name='ping', description='Checks bot ping')
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(f'Ping: {round(bot.latency * 1000)}ms')

@tree.command(name='sync', description='Syncs bot commands')
async def self(interaction: discord.Interaction):
    await tree.sync()
    await tree.sync(guild=guild)
    await interaction.response.send_message('Commands have been synced!')

@tree.command(name='define_verbose', description='Looks up the verbose definition(s) of a given word')
@app_commands.describe(
    word='Word to look up',
    spoiler='Whether you want the definition(s) to be spoiler-tagged or not'
    )
async def self(interaction: discord.Interaction, word: str, spoiler: bool=False):
    results = search_verbose(word)

    if 'error' in results:
        await interaction.response.send_message(f'Error: {results["error"]}')
        return
    
    title = results['word']
    embed = discord.Embed(title=title, colour=discord.Colour.random())
    for i, entry in enumerate(results['defs']):
        fl = entry['fl']
        _def = entry['def']
        name = f'{i+1}. ({fl}) ' + (f'||{_def}||' if spoiler else _def)

        value = ''
        if entry['ex']: value += '\nExample: ' + entry['ex']
        if entry['syn']: value += '\nSynonyms: ' + ', '.join(entry['syn'])
        if entry['ant']: value += '\nAntonyms: ' + ', '.join(entry['ant'])

        if not value: value = '\u200b'

        if len(name) > 256: name = (f'{name[:251]}...||' if spoiler else f'{name[:253]}...')
        if len(value) > 1024: value = value[:1021] + '...'
        
        embed.add_field(name=name, value=value, inline=False)

    await interaction.response.send_message(embed=embed)

@app_commands.describe(
    word='Word to look up',
    spoiler='Whether you want the definition(s) to be spoiler-tagged or not'
    )
@tree.command(name='define', description='Looks up the definition of a given word')
async def self(interaction: discord.Interaction, word: str, spoiler: bool=False):
    results = search(word)

    if 'error' in results:
        await interaction.response.send_message(f'Error: {results["error"]}')
        return
    
    if 'similar' in results:
        title = f'Couldn\'t find \'{word.lower()}\', did you mean:'
        embed = discord.Embed(title=title, colour=discord.Colour.random())
        for i, res in enumerate(results['similar']):
            name = f'{i+1}. {res}'
            if len(name) > 256: name = f'{name[:253]}...'
            embed.add_field(name=name, value='\u200b', inline=True)
        await interaction.response.send_message(embed=embed)
        return
    
    title = results['word']
    embed = discord.Embed(title=title, colour=discord.Colour.random())
    for i, entry in enumerate(results['defs']):
        fl = entry['fl']
        _def = entry['def']
        name = f'{i+1}. ({fl}) ' + (f'||{_def}||' if spoiler else _def)

        if len(name) > 256: name = (f'{name[:251]}...||' if spoiler else f'{name[:253]}...')

        value = '\u200b'

        embed.add_field(name=name, value=value, inline=False)

    await interaction.response.send_message(embed=embed)

@tree.command(name='add_word', description='Adds word to the dictionary database')
@app_commands.describe(
    word='Word to add'
    )
async def self(interaction: discord.Interaction, word: str):
    results = search(word)

    if 'error' in results:
        await interaction.response.send_message(f'Error: {results["error"]}')
        return

    if 'similar' in results:
        title = f'Couldn\'t find \'{word.lower()}\', did you mean:'
        embed = discord.Embed(title=title, colour=discord.Colour.random())
        for i, res in enumerate(results['similar']):
            name = f'{i+1}. {res}'
            if len(name) > 256: name = f'{name[:253]}...'
            embed.add_field(name=name, value='\u200b', inline=True)
        await interaction.response.send_message(embed=embed)
        return
    
    con = sqlite3.connect('lindow.db')
    cur = con.cursor()

    word = results['word']
    if cur.execute('SELECT * FROM dictionary WHERE word=?',(word,)).fetchone():
        con.close()
        await interaction.response.send_message(f'{word} has already been added')
        return

    for entry in results['defs']:
        fl = entry['fl']
        _def = entry['def'].replace('"','""')
        #print(f'word: {word}, def: {_def}, fl: {fl}')
        #data.append((word,_def,pos,'all'))
        cur.execute('INSERT INTO dictionary VALUES(?,?,?,"all")',(word,_def,fl))

    #res = cur.executemany('INSERT INTO dictionary VALUES(?,?,?,?)', data)
    con.commit()
    con.close()

    await interaction.response.send_message(f'{word} successfully added.')

@tree.command(name='remove_word', description='Remove word from the dictionary database')
@app_commands.describe(
    word='Word to remove'
    )
async def self(interaction: discord.Interaction, word: str):
    con = sqlite3.connect('lindow.db')
    cur = con.cursor()

    res = cur.execute('SELECT * FROM dictionary WHERE word=?', (word,))
    if not res.fetchone():
        con.close()
        await interaction.response.send_message(f'{word} not in database')
        return
        
    res = cur.execute('DELETE FROM dictionary WHERE word=?', (word,))
    con.commit()
    con.close()
    await interaction.response.send_message(f'{word} deleted from database')
    

@tree.command(name='quiz', description='Quizzes you on words stored in the database')
async def self(interaction: discord.Interaction):
    con = sqlite3.connect('lindow.db')
    cur = con.cursor()
    words = sample(cur.execute('SELECT DISTINCT word FROM dictionary').fetchall(), 4)
    options = []
    for word in words:
        stuff = choice(cur.execute('SELECT def,type FROM dictionary WHERE word=?',(word[0],)).fetchall())
        _def, _type = stuff
        options.append((word[0], _def, _type))
    
    #print(options)
    ans = randint(0,3)
    #print(ans)

    embed = discord.Embed(title=options[ans][0], colour=discord.Colour.random())
    for i, option in enumerate(options):
        _, _def, _type = option
        name = f'{"ABCD"[i]}) ({_type}) {_def}'
        if len(name) > 256: name = f'{name[:253]}...'
        embed.add_field(name=name, value='\u200b', inline=False)

    class MyView(View):
        @discord.ui.button(label='A', style=ButtonStyle.blurple)
        async def button1(self, interaction, button):
            for i in range(4):
                self.children[i].style = ButtonStyle.green if ans == i else ButtonStyle.red
                self.children[i].disabled = True
            button.emoji = '✔️' if button.style == ButtonStyle.green else '✖️'
            button.label = '\u200b'
            await interaction.response.edit_message(view=self)
        
        @discord.ui.button(label='B', style=ButtonStyle.blurple)
        async def button2(self, interaction, button):
            for i in range(4):
                self.children[i].style = ButtonStyle.green if ans == i else ButtonStyle.red
                self.children[i].disabled = True
            button.emoji = '✔️' if button.style == ButtonStyle.green else '✖️'
            button.label = '\u200b'
            await interaction.response.edit_message(view=self)
        
        @discord.ui.button(label='C', style=ButtonStyle.blurple)
        async def button3(self, interaction, button):
            for i in range(4):
                self.children[i].style = ButtonStyle.green if ans == i else ButtonStyle.red
                self.children[i].disabled = True
            button.emoji = '✔️' if button.style == ButtonStyle.green else '✖️'
            button.label = '\u200b'
            await interaction.response.edit_message(view=self)
        
        @discord.ui.button(label='D', style=ButtonStyle.blurple)
        async def button4(self, interaction, button):
            for i in range(4):
                self.children[i].style = ButtonStyle.green if ans == i else ButtonStyle.red
                self.children[i].disabled = True
            button.emoji = '✔️' if button.style == ButtonStyle.green else '✖️'
            button.label = '\u200b'
            await interaction.response.edit_message(view=self)
        
        async def interaction_check(self, view_interaction: discord.Interaction) -> bool:
            if interaction.user != view_interaction.user:
                await view_interaction.response.send_message(content='Go make your own quiz :P', ephemeral=True)
                return False
            return True

    view = MyView()
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(
    name='add_betterwords',
    description='Adds the first word of the `limit` most recent messages in betterwords to the dictionary database',
    guild=guild
    )
@app_commands.describe(
    limit='Number of messages to look for (default=1, range=1-100)'
    )
async def self(interaction: discord.Interaction, limit: int=1):
    limit = max(min(limit,100),1)
    betterwords = interaction.guild.get_channel(super_secret.betterwords_id)
    await interaction.response.defer()
    async for message in betterwords.history(limit=min(limit,100)):
        word = message.content.split(' ', 1)[0]
        if not word: continue
        print(f'trying to add {word}')
        results = search(word)
        if 'error' in results or 'similar' in results:
            print(f'adding {word} failed')
            continue
        
        con = sqlite3.connect('lindow.db')
        cur = con.cursor()

        word = results['word']
        if cur.execute('SELECT * FROM dictionary WHERE word=?',(word,)).fetchone():
            print(f'{word} already added')
            continue

        for entry in results['defs']:
            fl = entry['fl']
            _def = entry['def']
            #data.append((word,_def,pos,'all'))
            cur.execute('INSERT INTO dictionary VALUES(?,?,?,"all")',(word,_def,fl))

        #res = cur.executemany('INSERT INTO dictionary VALUES(?,?,?,?)', data)
        con.commit()
        con.close()
        print(f'{word} added')
    
    await interaction.followup.send('Good job, a whole bunch of words were probably added')

@tree.command(name='listwords', description='Lists all of the words stored in the database')
async def self(interaction: discord.Interaction):
    con = sqlite3.connect('lindow.db')
    cur = con.cursor()

    embed = discord.Embed(title='Word List', colour=discord.Colour.random())
    res = cur.execute('SELECT DISTINCT word FROM dictionary ORDER BY word COLLATE NOCASE ASC')
    name = ''
    words = []
    for word in res.fetchall():
        word = word[0]
        if word[0].upper() != name:
            if name:
                value = ', '.join(words)
                if len(value) > 1024: value = value[:1021] + '...'
                embed.add_field(name=name, value=value, inline=False)
                words = []
            name = word[0].upper()
        words.append(word)
    
    con.close()
    await interaction.response.send_message(embed=embed)

@tree.command(
    name='listwords_prefix',
    description='Lists all of the words stored in the database starting with *prefix*'
    )
@app_commands.describe(
    prefix='Prefix to search for'
)
async def self(interaction: discord.Interaction, prefix: str):
    prefix = ''.join(c for c in prefix.lower() if c.isalnum() or c in ' -')
    con = sqlite3.connect('lindow.db')
    cur = con.cursor()

    embed = discord.Embed(title='Word List', colour=discord.Colour.random())
    res = cur.execute(f'SELECT DISTINCT word FROM dictionary WHERE word GLOB \'[{prefix[0].capitalize()}{prefix[0]}]{prefix[1:]}*\' ORDER BY word COLLATE NOCASE ASC')
    
    name = prefix
    words = [word[0] for word in res.fetchall()]
    value = ', '.join(words)
    if len(name) > 256: name = f'{name[:253]}...'
    if len(value) > 1024: value = value[:1021] + '...'

    if not value: value = '\u200b'
    embed.add_field(name=name, value=value, inline=False)
    
    con.close()
    await interaction.response.send_message(embed=embed)

@tree.command(name='test', description='Test stuff')
@app_commands.describe(
    choices='Classic rock-paper-scissors dilemma'
)
@app_commands.choices(choices=[
    app_commands.Choice(name="Rock", value="rock"),
    app_commands.Choice(name="Paper", value="paper"),
    app_commands.Choice(name="Scissors", value="scissors"),
    ])
async def self(interaction: discord.Interaction, choices: app_commands.Choice[str]=None):
    if choices.value == 'rock':
        await interaction.response.send_message('I picked paper, you lose!')
    elif choices.value == 'paper':
        await interaction.response.send_message('I picked scissors, you lose!')
    elif choices.value == 'scissors':
        await interaction.response.send_message('I picked rock, you lose!')
    else:
        await interaction.response.send_message('You forgot to pick something loser')

bot.run(super_secret.token)