# Who's that Pokemon!?!

from pokemon import *

import sys
import random
from os.path import exists

from PIL import Image

# import csv
import json

if __name__ == '__main__':
    # Default
    first_pokemon = 1
    last_pokemon = 905
    num_choices = 5

    # From command line
    num_args = len(sys.argv)
    if num_args > 2:
        first_pokemon = int(sys.argv[1])
        last_pokemon = int(sys.argv[2])
        if num_args > 3:
            num_choices = int(sys.argv[3])

    while True:
        # Pool of Pokemon
        pokemon_numbers =list(range(first_pokemon, last_pokemon + 1))
        random.shuffle(pokemon_numbers)
    
        print("== Who's That Pokemon!?! ==")
    
        # Load pokedex, converting string keys to integer
        dex = {int(k):v for k,v in json.load(open('pokedex.json')).items()}
    
        choices = pokemon_numbers[:num_choices]
        random.shuffle(choices)
        letter = 'A'
    
        for choice in choices:
            print( f"{letter}: {dex[choice]['name']}")
            letter = chr(ord(letter) + 1)
    
        answer = dex[pokemon_numbers[0]]
        # pprint.pprint(answer)
        string = format(pokemon_numbers[0], "03d")
        # suffix = 'k135_1a32_1s0_r02_q08'
        # filename = f'art/art_{string}_{suffix}.png'
        filename = f'art/art_{string}_image.png'
    
        if not exists(filename):
            p = Pokemon(pokemon_numbers[0])
            time_print(p.chart.save,"Chart is missing. Generating... ",filename, quiet=True)
            del p
    
        print('* Showing clue. Close to reveal answer *', end='\r')
        image = Image.open(filename)
        image.show()
    
        print('                                        ')
        print(f"== {answer['name']} ==")
        print(answer['description']+'\n')
    
        answer = Image.open(f'art/art_{string}.png')
        answer.show()
