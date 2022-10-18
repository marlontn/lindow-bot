import requests
import json
from super_secret import api_key

word = 'prescienc'
url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}'

r = requests.get(url)
print(r.status_code)
print(type(r))
res = r.json()
print(len(res))
print(res)

for key in res:
    print(json.dumps(key,indent=2))

i = 1
for entry in res:
    defo = entry['meta']['id'].lower().split(':')[0]
    print(defo)
    if defo != word.lower(): continue
    fl = entry.get('fl','N/A')
    print(f'({fl}):')
    for definition in entry['shortdef']:
        print(f'{i}. {definition}')
        i += 1

'''
figure of speech: res['fl']

definition: for def in res['def']:

audio: https://media.merriam-webster.com/audio/prons/[language_code]/[country_code]/[format]/[subdirectory]/[base filename].[format]
audio_val = res['hwi']['prs'][0]['sound']['audio']
[language_code] = 'en'
[country_code] = 'us'
[format] = 'mp3' or 'wav' or 'ogg'
[subdirectory]:
    = 'bix' if audio_val.startswith('bix')
    = 'gg' if audio_val.startswith('gg')
    = 'number' if audio_val.startswith([0-9] or [string.punctuation])
    = audio_val[0] otherwise
[base_filename] = audio_val
'''

'''
r = requests.get('https://api.dictionaryapi.dev/api/v2/entries/en/dark')
res = r.json()[0]

for key in res:
    print(f'{key} : {res[key]}')
    print()

print(res['word'])
#print(res['origin'])
for meaning in res['meanings']:
    print(meaning['partOfSpeech'])
    for definition in meaning['definitions']:
        print(definition['definition'])
        if 'example' in definition: print(definition['example'])
        print(definition['synonyms'])
        print(definition['antonyms'])
'''