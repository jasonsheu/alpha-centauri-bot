import discord
import os
from nltk.util import everygrams
from nltk.lm.preprocessing import pad_both_ends
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.lm import MLE
from keep_alive import keep_alive

import re
import random

client = discord.Client()
#cleaning
ttalk_fp = os.path.join('ttalk.txt')
ttalk = open(ttalk_fp, encoding='utf-8').read()
ttalk = re.sub(r'\n', ' ', ttalk)
ttalk = re.sub(r'<[\#\@][!0-9]+>', ' ', ttalk)
ttalk = re.sub(r'<\w*:[A-Za-z0-9\_]+:\d+>', ' ', ttalk)
tokenized = [list(map(str.lower, word_tokenize(word))) for word in sent_tokenize(ttalk)]
#model training, trigrams
train, padded = padded_everygram_pipeline(3, tokenized)
model = MLE(3)
model.fit(train, padded)


#word generation
def generate_random_sentence(model, n_words):
    detokenize = TreebankWordDetokenizer().detokenize
    sentence = []
    for word in model.generate(n_words, random_seed = random.randint(-1000000, 1000000)):
        if word == '<s>':
            continue
        if word =='</s>':
            break
        sentence.append(word)
    
    return detokenize(sentence)

#finishing a sentence
def finish_sentence(model, n_words, start):
    detokenize = TreebankWordDetokenizer().detokenize
    sentence = []
    sentence.append(start)
    for word in model.generate(n_words, text_seed = start.split(), random_seed = random.randint(-1000000, 1000000)):
        if word == '<s>':
            continue
        if word =='</s>':
            break
        sentence.append(word)
    
    return detokenize(sentence)


@client.event
async def on_ready():
    print("I'm in")
    print(client.user)

@client.event
async def on_message(message):
    random_length = random.randint(10, 50)
    if message.content.startswith('ac!generate'):
        if message.author != client.user:
            await message.channel.send(generate_random_sentence(model, random_length))
    
    if message.content.startswith('ac!complete "'):
        to_complete = message.content[13:]
        stripped = to_complete.strip('"')
        if message.author != client.user:
            await message.channel.send(finish_sentence(model, random_length, stripped))
    if message.content.startswith('ac!complete') and message.content[12] != '"':
        
        if message.author != client.user:
            await message.channel.send('add quotation marks around your text silly')

keep_alive
token = os.environ.get("DISCORD_BOT_SECRET")
client.run(token)