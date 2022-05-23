# Who's that Pokemon!?!

from pokemon import *
import argparse
import random
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Which Pokemon?')
    parser.add_argument('-f', '--first', type=int, default=POKE_GENS[1][0])
    parser.add_argument('-l', '--last', type=int, default=POKE_GENS[1][1])
    parser.add_argument('-g', '--gen', type=int, default=None)
    parser.add_argument('-s', '--starters', action='store_true')
    parser.add_argument('-c', '--choices', type=int, default=5)
    args = parser.parse_args() # read in args
    if args.gen is not None:
        args.first, args.last = POKE_GENS[args.gen]
    poke_numbers = list(range(args.first, args.last + 1))
    if args.starters:
        poke_numbers = [x for x in poke_numbers if x in POKE_STARTERS]
    print(f'First: {args.first}, Last: {args.last}, Total: {len(poke_numbers)}')

    while True:
        random.shuffle(poke_numbers)
    
        print("== Who's That Pokemon!?! ==")
    
        # Load pokedex, converting string keys to integer
        dex = {int(k):v for k,v in json.load(open('pokedex.json')).items()}
    
        choices = poke_numbers[:args.choices] # take first n elements from list
        random.shuffle(choices)
        for n, choice in enumerate(choices):
            print( f"{chr(ord('A') + n)}: {dex[choice]['name']}")
    
        answer = dex[poke_numbers[0]]
        string = format(poke_numbers[0], "03d")
        filename = f'art/art_{string}_image.png'
    
        if not exists(filename):
            p = Pokemon(poke_numbers[0])
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
