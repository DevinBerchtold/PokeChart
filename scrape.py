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
    # Not neccessary right now
}
# PokeAPI IDs don't match Serebii IDs for last gen so we convert ID to names
pokemon_names = {
    906: 'sprigatito', 907: 'floragato', 908: 'meowscarada', 909: 'fuecoco', 910: 'crocalor', 911: 'skeledirge', 912: 'quaxly', 913: 'quaxwell', 914: 'quaquaval', 915: 'lechonk', 916: 'oinkologne', 917: 'tarountula',
    918: 'spidops', 919: 'nymble', 920: 'lokix', 921: 'pawmi', 922: 'pawmo', 923: 'pawmot', 924: 'tandemaus', 925: 'maushold', 926: 'fidough', 927: 'dachsbun', 928: 'smoliv', 929: 'dolliv', 
    930: 'arboliva', 931: 'squawkabilly', 932: 'nacli', 933: 'naclstack', 934: 'garganacl', 935: 'charcadet', 936: 'armarouge', 937: 'ceruledge', 938: 'tadbulb', 939: 'bellibolt', 940: 'wattrel', 941: 'kilowattrel', 
    942: 'maschiff', 943: 'mabosstiff', 944: 'shroodle', 945: 'grafaiai', 946: 'bramblin', 947: 'brambleghast', 948: 'toedscool', 949: 'toedscruel', 950: 'klawf', 951: 'capsakid', 952: 'scovillain', 953: 'rellor', 
    954: 'rabsca', 955: 'flittle', 956: 'espathra', 957: 'tinkatink', 958: 'tinkatuff', 959: 'tinkaton', 960: 'wiglett', 961: 'wugtrio', 962: 'bombirdier', 963: 'finizen', 964: 'palafin', 965: 'varoom',
    966: 'revavroom', 967: 'cyclizar', 968: 'orthworm', 969: 'glimmet', 970: 'glimmora', 971: 'greavard', 972: 'houndstone', 973: 'flamigo', 974: 'cetoddle', 975: 'cetitan', 976: 'veluza', 977: 'dondozo', 
    978: 'tatsugiri', 979: 'annihilape', 980: 'clodsire', 981: 'farigiraf', 982: 'dudunsparce', 983: 'kingambit', 984: 'great-tusk', 985: 'scream-tail', 986: 'brute-bonnet', 987: 'flutter-mane', 988: 'slither-wing',
    989: 'sandy-shocks', 990: 'iron-treads', 991: 'iron-bundle', 992: 'iron-hands', 993: 'iron-jugulis', 994: 'iron-moth', 995: 'iron-thorns', 996: 'frigibax', 997: 'arctibax', 998: 'baxcalibur', 999: 'gimmighoul',
    1000: 'gholdengo', 1001: 'wo-chien', 1002: 'chien-pao', 1003: 'ting-lu', 1004: 'chi-yu', 1005: 'roaring-moon', 1006: 'iron-valiant', 1007: 'koraidon', 1008: 'miraidon'
}

headers = {
    'User-Agent': 'PokeChart (https://github.com/DevinBerchtold/PokeChart/, v0.0.2)',
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

    if num in pokemon_names: # If we have a name, access by name instead of ID
        pokemon_species = get(f'https://pokeapi.co/api/v2/pokemon-species/{pokemon_names[num]}/')
        pokemon_data = get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_names[num]}')
    else:
        pokemon_species = get(f'https://pokeapi.co/api/v2/pokemon-species/{num}/')
        pokemon_data = get(f'https://pokeapi.co/api/v2/pokemon/{num}')
    pokemon = {k: pokemon_data[k] for k in ('id', 'name')}

    pokemon['types'] = [t['type']['name'] for t in pokemon_data['types']]
    pokemon['stats'] = {s['stat']['name']: s['base_stat'] for s in pokemon_data['stats']}

    for n in pokemon_species['names']:
        if n['language']['name'] == lang:
            pokemon['name'] = n['name']

    # Get first flavor text from this list (oldest for each pokemon)
    versions = ["red","blue","yellow","gold","silver","crystal","ruby","sapphire","emerald","diamond","pearl","platinum","black","white","x","y","sun","moon","sword","shield","scarlet","violet","legends-arceus"]
    # versions = reversed(versions) # newest
    if pokemon_species['flavor_text_entries']:
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
        dex_source = f'(???):'.ljust(11)
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
if not os.path.exists('game'):
    os.makedirs('game')
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

            # curl https://www.serebii.net/swordshield/pokemon/[001-905].png -o "game_#1.png"
            if n <= 905:
                save_file(f'https://www.serebii.net/swordshield/pokemon/{n:03d}.png', f'game/game_{n:03d}.png')
            else: # New gen images are under different URL
                save_file(f'https://www.serebii.net/scarletviolet/pokemon/{n:03d}.png', f'game/game_{n:03d}.png')
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            print(f'Exception on {n}. (Serebii is mad)')
            break

        print('')

        # Only add to dictionary if all data is gathered
        dex[s] = pokemon

# We get here either by getting to the end of the list or encountering and exception
json.dump(dex, open('pokedex.json', 'w'), indent='\t')
print(f'Wrote pokedex.json with {len(dex)} Pokemon')


# # YAML copy for readability
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