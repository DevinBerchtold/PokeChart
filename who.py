# Who's that Pokemon!?!

from pokemon import *
import random
import json

def print_over(string):
    print('\033[1A'+string+'\033[K')

if __name__ == '__main__':
    args = Pokemon.get_args()
    poke_numbers = args.numbers

    # Load pokedex, converting string keys to integer
    dex = {int(k):v for k,v in json.load(open('pokedex.json')).items()}    

    while True:
        random.shuffle(poke_numbers)
    
        print_over("== Who's That Pokemon!?! ==")
    
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
    
        # print('* Showing clue. Close to reveal answer *', end='\r')
        image = Image.open(filename)
        image.show()
        input('Press enter to reveal answer...')
    
        print_over('                                        ')
        print(f"== {answer['name']} ==")
        print(answer['description']+'\n')
    
        answer = Image.open(f'art/art_{string}.png')
        answer.show()
        input('Press enter to continue...')
