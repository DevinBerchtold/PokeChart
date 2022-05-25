import json
import argparse
from chart import *



 ######   #######  ##    ##  ######  ########    ###    ##    ## ########  ######
##    ## ##     ## ###   ## ##    ##    ##      ## ##   ###   ##    ##    ##    ##
##       ##     ## ####  ## ##          ##     ##   ##  ####  ##    ##    ##
##       ##     ## ## ## ##  ######     ##    ##     ## ## ## ##    ##     ######
##       ##     ## ##  ####       ##    ##    ######### ##  ####    ##          ##
##    ## ##     ## ##   ### ##    ##    ##    ##     ## ##   ###    ##    ##    ##
 ######   #######  ##    ##  ######     ##    ##     ## ##    ##    ##     ######

IMAGE_PREFIXES = [('art', 1, 32), ('ss', 1, 0)]
# for prefix, weight, remove_black in IMAGE_PREFIXES:
#     PREFIX_STRING += str(weight) + prefix[0] + str(remove_black) + '_'

POKE_TYPES = ['grass', 'poison', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic', 'rock', 'steel', 'ice', 'ghost', 'dragon', 'dark']
POKE_STATS = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']
# Pokemon numbers to process
POKE_GENS = {
    0: (1, 905), # All generations
    1: (1, 151),
    2: (152, 251),
    3: (252, 386),
    4: (387, 493),
    5: (494, 649),
    6: (650, 721),
    7: (722, 807),
    8: (808, 905)
}
POKE_STARTERS = []
for x in [1, 152, 252, 387, 495, 650, 722, 810]:
    POKE_STARTERS += range(x, x + 9)



########   #######  ##    ## ######## ##     ##  #######  ##    ##
##     ## ##     ## ##   ##  ##       ###   ### ##     ## ###   ##
##     ## ##     ## ##  ##   ##       #### #### ##     ## ####  ##
########  ##     ## #####    ######   ## ### ## ##     ## ## ## ##
##        ##     ## ##  ##   ##       ##     ## ##     ## ##  ####
##        ##     ## ##   ##  ##       ##     ## ##     ## ##   ###
##         #######  ##    ## ######## ##     ##  #######  ##    ##

class Pokemon:
    """Instances describe a Pokemon with a Pokedex number.

    Attributes:
        dex: Dictionary of all Pokemon information by Pokedex number.
    """
    dex = {int(k):v for k,v in json.load(open('pokedex.json')).items()}

    all_colors = Colors()
    type_charts = {}
    type_groups = {}
    for t in POKE_TYPES:
        type_charts[t] = Chart()
        type_groups[t] = []

    def get_args():
        """Parse and return Pokemon arguments and a list of Pokemon"""
        parser = argparse.ArgumentParser(description='Which Pokemon?')
        parser.add_argument('-n', '--num', type=str, default='1-151', help="format: -n1-151")
        parser.add_argument('-g', '--gen', type=int)
        parser.add_argument('-s', '--starters', action='store_true')
        parser.add_argument('-c', '--choices', type=int, default=5)
        args = parser.parse_args() # read in args
        if args.num is not None:
            args.first, args.last = list(map(int,args.num.split('-')))
        if args.gen is not None:
            args.first, args.last = POKE_GENS[args.gen]
        pokes = list(range(args.first, args.last + 1))
        if args.starters:
            args.numbers = [x for x in pokes if x in POKE_STARTERS]
        else:
            args.numbers = pokes
        print(f'First: {args.first}, Last: {args.last}, Total: {len(args.numbers)}')
        return args

    def __init__(self, number: int, prefix: str='art/art_', suffix: str='.png'):
        """Create `Pokemon` from Pokedex number `number`.

        Args:
            number: The Pokedex number to generate the Pokemon from.
            prefix: Output filename prefix.
            suffix: Output filename suffix.
        """
        # get stats and data from json file
        self.number = number
        self.string = format(number, "03d")
        self.dex = Pokemon.dex[number]
        self.name = self.dex['name']
        self.types = self.dex['types']
        if 'description' in self.dex:
            self.description = self.dex['description']
        if len(self.types) == 2:
            self.type1 = self.types[0]
            self.type2 = self.types[1]
        else:
            self.type1 = self.types[0]
            self.type2 = ''

        self.stats = self.dex['stats']

        # self.type_relations = {}
        self.filename = prefix+self.string+suffix
        self.chartname = prefix+self.string+'_image'+suffix

        self._printline = f'#{self.string} {self.name}:'.ljust(17)

        # get color data for pokemon
        self.chart = Chart()
        for prefix, weight, threshold in IMAGE_PREFIXES:
            image_file = prefix+'/'+ prefix + '_' + self.string + '.png'
            self.chart.addImage(image_file, weight)
            self.chart.removeBlack(threshold)
        self.chart.removeFraction(float(COLOR_REMOVE)/100.0)

        # all pokemon color dictionary
        Pokemon.all_colors.addDict(self.chart)
        # type color dictionarys
        frac = 1.0
        if self.type2 != '':
            frac = 0.5
            Pokemon.type_groups[self.type2].append(self)
            Pokemon.type_charts[self.type2].addDict(self.chart, frac)
        Pokemon.type_groups[self.type1].append(self)
        Pokemon.type_charts[self.type1].addDict(self.chart, frac)

    def __str__(self):
        return self._printline