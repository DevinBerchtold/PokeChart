# py {file}
# C:\Program Files (x86)\Python36-32\Scripts>pip.exe install png
# import string
# import csv
# from pokedex.py import pokedex
import json
from chart import *



 ######   #######  ##    ##  ######  ########    ###    ##    ## ########  ######
##    ## ##     ## ###   ## ##    ##    ##      ## ##   ###   ##    ##    ##    ##
##       ##     ## ####  ## ##          ##     ##   ##  ####  ##    ##    ##
##       ##     ## ## ## ##  ######     ##    ##     ## ## ## ##    ##     ######
##       ##     ## ##  ####       ##    ##    ######### ##  ####    ##          ##
##    ## ##     ## ##   ### ##    ##    ##    ##     ## ##   ###    ##    ##    ##
 ######   #######  ##    ##  ######     ##    ##     ## ##    ##    ##     ######

DEBUG = False

TOTAL_TIME = 0.0
PREFIX_STRING = ''
#IMAGE_PREFIXES = ['small', 'front', 'anime']
# IMAGE_PREFIXES = [('art', 1, 32), ('icon', 0, 4), ('ss', 1, 0)]
IMAGE_PREFIXES = [('art', 1, 32), ('ss', 1, 0)]
# for prefix, weight, remove_black in IMAGE_PREFIXES:
#     PREFIX_STRING += str(weight) + prefix[0] + str(remove_black) + '_'

# Don't edit these
# POKEMON_TYPES = ['Grass', 'Poison', 'Fire', 'Flying', 'Water', 'Bug', 'Normal', 'Electric', 'Ground', 'Fairy', 'Fighting', 'Psychic', 'Rock', 'Steel', 'Ice', 'Ghost', 'Dragon', 'Dark']
# POKEMON_STATS = ['AllStats', 'HP', 'Attack', 'Defense', 'SpAtk', 'SpDef', 'Speed']
POKEMON_TYPES = ['grass', 'poison', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic', 'rock', 'steel', 'ice', 'ghost', 'dragon', 'dark']
POKEMON_STATS = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']



########   #######  ##    ## ######## ##     ##  #######  ##    ##
##     ## ##     ## ##   ##  ##       ###   ### ##     ## ###   ##
##     ## ##     ## ##  ##   ##       #### #### ##     ## ####  ##
########  ##     ## #####    ######   ## ### ## ##     ## ## ## ##
##        ##     ## ##  ##   ##       ##     ## ##     ## ##  ####
##        ##     ## ##   ##  ##       ##     ## ##     ## ##   ###
##         #######  ##    ## ######## ##     ##  #######  ##    ##

class Pokemon:
    dex = {int(k):v for k,v in json.load(open('pokedex.json')).items()}

    all_colors = Colors()
    type_charts = {}
    type_groups = {}
    for t in POKEMON_TYPES:
        type_charts[t] = Chart()
        type_groups[t] = []

    def __init__(self, number, prefix='art/art_', suffix='.png'):
        # get stats and data from csv file
        self.number = number
        self.string = format(number, "03d")
        # self.name, self.type1, self.type2 = csv_dict[str(self.number)][:3]
        self.name = Pokemon.dex[number]['name']
        self.types = Pokemon.dex[number]['types']
        if len(self.types) == 2:
            self.type1 = self.types[0]
            self.type2 = self.types[1]
        else:
            self.type1 = self.types[0]
            self.type2 = ''

        self.stats = Pokemon.dex[number]['stats']

        # self.type_relations = {}
        self.filename = prefix+self.string+suffix
        self.chartname = prefix+self.string+'_image'+suffix

        self._printline = f'#{self.string} {self.name}:'.ljust(17)

        # get color data for pokemon
        self.chart = Chart()
        for prefix, weight, threshold in IMAGE_PREFIXES:
            image_file = prefix+'/'+ prefix + '_' + self.string + '.png'
            # if DEBUG: iprint(f'Opening {image_file}')
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