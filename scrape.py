# Download data and store locally

import json
import time
import requests
import os
from pokemon import Pokemon
# import yaml



 ######   #######  ##    ##  ######  ########    ###    ##    ## ########  ######
##    ## ##     ## ###   ## ##    ##    ##      ## ##   ###   ##    ##    ##    ##
##       ##     ## ####  ## ##          ##     ##   ##  ####  ##    ##    ##
##       ##     ## ## ## ##  ######     ##    ##     ## ## ## ##    ##     ######
##       ##     ## ##  ####       ##    ##    ######### ##  ####    ##          ##
##    ## ##     ## ##   ### ##    ##    ##    ##     ## ##   ###    ##    ##    ##
 ######   #######  ##    ##  ######     ##    ##     ## ##    ##    ##     ######

# These aren't in PokeDexAPI yet
pokemon_overrides = {
    '899': {
        'id': 899,
        'name': 'Wyrdeer',
        'types': ['normal', 'psychic'],
        'stats': {'hp': 103, 'attack': 105, 'defense': 72, 'special-attack': 105, 'special-defense': 75, 'speed': 65},
        'description': "The black orbs shine with an uncanny light when the\nPok\u00e9mon is erecting invisible barriers. The fur\nshed from its beard retains heat well and is a\nhighly useful material for winter clothing."
    },
    '900': {
        'id': 900,
        'name': 'Kleavor',
        'types': ['bug', 'rock'],
        'stats': {'hp': 70, 'attack': 135, 'defense': 95, 'special-attack': 45, 'special-defense': 70, 'speed': 85},
        'description': "A violent creature that fells towering trees with\nits crude axes and shields itself with hard stone.\nIf one should chance upon this Pok\u00e9mon in the\nwilds, one's only recourse is to flee."
    },
    '901': {
        'id': 901,
        'name': 'Ursaluna',
        'types': ['normal', 'ground'],
        'stats': { 'hp': 130, 'attack': 140, 'defense': 105, 'special-attack': 45, 'special-defense': 80, 'speed': 50},
        'description': "I believe it was Hisui's swampy terrain that gave\nUrsaluna its burly physique and newfound capacity\nto manipulate peat at will."
    },
    '902': {
        'id': 902,
        'name': 'Basculegion: Male',
        'types': ['water', 'ghost'],
        'stats': { 'hp': 120, 'attack': 112, 'defense': 65, 'special-attack': 80, 'special-defense': 75, 'speed': 78},
        'description': "Clads itself in the souls of comrades that perished\nbefore fulfilling their goals of journeying\nupstream. No other species throughout all Hisui's\nrivers is Basculegion's equal."
    },
    '903': {
        'id': 903,
        'name': 'Sneasler',
        'types': ['poison', 'fighting'],
        'stats': { 'hp': 80, 'attack': 130, 'defense': 60, 'special-attack': 40, 'special-defense': 80, 'speed': 120},
        'description': "Because of Sneasler's virulent poison and daunting\nphysical prowess, no other species could hope to\nbest it on the frozen highlands. Preferring\nsolitude, this species does not form packs."
    },
    '904': {
        'id': 904,
        'name': 'Overqwil',
        'types': ['dark', 'poison'],
        'stats': { 'hp': 85, 'attack': 115, 'defense': 95, 'special-attack': 65, 'special-defense': 65, 'speed': 85},
        'description': "Its lancelike spikes and savage temperament have\nearned it the nickname \"sea fiend.\" It slurps up\npoison to nourish itself."
    },
    '905': {
        'id': 905,
        'name': 'Enamorous: Incarnate Forme',
        'types': ['fairy', 'flying'],
        'stats': { 'hp': 74, 'attack': 115, 'defense': 70, 'special-attack': 135, 'special-defense': 80, 'speed': 106},
        'description': "When it flies to this land from across the sea,\nthe bitter winter comes to an end. According to\nlegend, this Pok\u00e9mon's love gives rise to the\nbudding of fresh life across Hisui."
    },
}

headers = {
    'User-Agent': 'Pokemon Colors (https://???.com/, v0.0.1)',
    'Accept': 'application/json'
}

def get(path):
    res = requests.get(path, headers=headers)
    if res.ok:
        return res.json()
    else:
        return res.raise_for_status()

def get_pokemon(num):
    # https://pokeapi.co/api/v2/pokemon/{id or name}/
    lang = 'en'
    global dex_source
    pokemon_species = get(f'https://pokeapi.co/api/v2/pokemon-species/{num}/')
    pokemon_data = get(f'https://pokeapi.co/api/v2/pokemon/{num}')
    pokemon = {k: pokemon_data[k] for k in ('id', 'name')}

    pokemon['types'] = [t['type']['name'] for t in pokemon_data['types']]
    pokemon['stats'] = {s['stat']['name']: s['base_stat'] for s in pokemon_data['stats']}

    for n in pokemon_species['names']:
        if n['language']['name'] == lang:
            pokemon['name'] = n['name']

    # Get first flavor text from this list (oldest for each pokemon)
    versions = ["red","blue","yellow","gold","silver","crystal","ruby","sapphire","emerald","diamond","pearl","platinum","black","white","x","y","sun","moon","sword","shield"]
    # versions = reversed(versions) # newest
    for v in versions:
        for n in pokemon_species['flavor_text_entries']:
            if n['language']['name'] == lang:
                if n['version']['name'] == v:
                    pokemon['description'] = n['flavor_text'].replace('\x0c', '\n')
                    dex_source = f'({v}):'.ljust(11)
                    break
        else:
            continue
        break
    if 'description' not in pokemon:
        pokemon['description'] = 'Description unavailable'
    return pokemon

def save_file(url, filename):
    if os.path.exists(filename):
        print(f'{url} ==> {filename} already exists')
    else:
        file = requests.get(url).content
        with open(filename, 'wb') as handler:
            handler.write(file)
        print(f'{url} ==> {filename} saved')



##     ##    ###    #### ##    ##
###   ###   ## ##    ##  ###   ##
#### ####  ##   ##   ##  ####  ##
## ### ## ##     ##  ##  ## ## ##
##     ## #########  ##  ##  ####
##     ## ##     ##  ##  ##   ###
##     ## ##     ## #### ##    ##

args = Pokemon.get_args()

dex = {}
if os.path.exists('pokedex.json'):
    dex = json.load(open('pokedex.json'))

# Create directories if they don't exist
if not os.path.exists('art'):
    os.makedirs('art')
if not os.path.exists('ss'):
    os.makedirs('ss')
if not os.path.exists('output'):
    os.makedirs('output')

for n in args.numbers:
    print(f'Pokemon #{n}')
    s = str(n)
    if s not in dex:
        if s in pokemon_overrides:
            pokemon = pokemon_overrides[s]
            print(f"Dex (hardcode): {pokemon['id']} {pokemon['name']} ({', '.join(pokemon['types'])})")
        else:
            try:
                pokemon = get_pokemon(n)
                time.sleep(0.1) # Slow it down so they don't get mad
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
                print(f'Exception on #{n}. (Pokedex is mad)')
                break
            
            print(f"Dex {dex_source} {pokemon['id']} {pokemon['name']} ({', '.join(pokemon['types'])})")

        try:
            # curl https://www.serebii.net/pokemon/art/[001-905].png -o "art_#1.png"
            save_file(f'https://www.serebii.net/pokemon/art/{n:03d}.png', f'art/art_{n:03d}.png')

            # curl https://www.serebii.net/swordshield/pokemon/[001-905].png -o "ss_#1.png"
            save_file(f'https://www.serebii.net/swordshield/pokemon/{n:03d}.png', f'ss/ss_{n:03d}.png')
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            print(f'Exception on {n}. (Serebii is mad)')
            break

        print('')

        # Only add to dictionary if all data is gathered
        dex[s] = pokemon

# We get here either by getting to the end of the list or encountering and exception
json.dump(dex, open('pokedex.json', 'w'), indent='\t')
print(f'Wrote pokedex.json with {len(dex)} Pokemon')


# YAML copy for readability
# def str_presenter(dumper, data):
#     if len(data) > 40:
#         return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='\"')
#     else:
#         return dumper.represent_scalar('tag:yaml.org,2002:str', data)

# def list_presenter(dumper, data):
#     return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

# def dict_presenter(dumper, data):
#     if list(data.keys()) == ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']:
#         return dumper.represent_mapping('tag:yaml.org,2002:map', data, flow_style=True)
#     else:
#         return dumper.represent_mapping('tag:yaml.org,2002:map', data, flow_style=False)

# yaml.representer.SafeRepresenter.add_representer(str, str_presenter)
# yaml.representer.SafeRepresenter.add_representer(list, list_presenter)
# yaml.representer.SafeRepresenter.add_representer(dict, dict_presenter)

# yaml.safe_dump(dex, open('pokedex.yaml', 'w'), width=320, allow_unicode=False, sort_keys=False, default_flow_style=None)
# print(f'Wrote pokedex.yaml with {len(dex)} Pokemon')