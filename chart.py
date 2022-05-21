from PIL import Image
from PIL import ImageDraw
#from matplotlib import docstring
# from sklearn.cluster import KMeans
# from sklearn.cluster import MiniBatchKMeans
import sklearn.cluster as cluster
import matplotlib.pyplot as plt
import numpy as np
import itertools as it
import multiprocessing as mp
import time
import math
from os.path import exists

 ######   #######  ##    ##  ######  ########    ###    ##    ## ########  ######
##    ## ##     ## ###   ## ##    ##    ##      ## ##   ###   ##    ##    ##    ##
##       ##     ## ####  ## ##          ##     ##   ##  ####  ##    ##    ##
##       ##     ## ## ## ##  ######     ##    ##     ## ## ## ##    ##     ######
##       ##     ## ##  ####       ##    ##    ######### ##  ####    ##          ##
##    ## ##     ## ##   ### ##    ##    ##    ##     ## ##   ###    ##    ##    ##
 ######   #######  ##    ##  ######     ##    ##     ## ##    ##    ##     ######

DEBUG = False

# CORES = 1
CORES = 4
# CORES = 6
# CORES = 10

CHART_SIZE = 512
CHART_KS = (1, 3, 5)

# CHART_SUPERSAMPLE = 4
CHART_SUPERSAMPLE = 16 # More than 16 doesn't do anything

FLOAT_MAX = 1.0e+64
COLOR_REMOVE = 2
# COLOR_QUANTIZE = 1
COLOR_QUANTIZE = 8
COLOR_TRANSPARENT = (255, 255, 255, 0)

GLOBAL_TABS = 0

def iprint(string):
    if (string[0] != '<') and (string[0] != '>'):
        string = ' '+string
    print(('  '*GLOBAL_TABS)+string)

def unique_cyclic_permutations(thing, length):
    if length == 0:
        yield (); return
    for x in it.permutations(thing[1:], length - 1):
        yield (thing[0],) + x
    if length < len(thing):
        yield from unique_cyclic_permutations(thing[1:], length)

def time_print(func, string, *args, **kwargs):
    print(string, end='\r')
    t0 = time.time()
    ret = func(*args, **kwargs)
    print(f"{string}{time.time()-t0:.3f}s")
    return ret

def timed(func):
    def wrapper(*args, **kwargs):
        global GLOBAL_TABS

        if DEBUG:
            iprint(f">> {func.__name__}({args=}, {kwargs=})")

            GLOBAL_TABS += 1
            start_time = time.time()

        result = func(*args, **kwargs)

        if DEBUG:
            end_time = time.time()
            GLOBAL_TABS -= 1

            if result:
                iprint(f"<< {func.__name__} took {(end_time - start_time):.3f}s and returned a {type(result)}")
            else:
                iprint(f"<< {func.__name__} took {(end_time - start_time):.3f}s")

        return result

    return wrapper



 ######   #######  ##        #######  ########   ######
##    ## ##     ## ##       ##     ## ##     ## ##    ##
##       ##     ## ##       ##     ## ##     ## ##
##       ##     ## ##       ##     ## ########   ######
##       ##     ## ##       ##     ## ##   ##         ##
##    ## ##     ## ##       ##     ## ##    ##  ##    ##
 ######   #######  ########  #######  ##     ##  ######

class Colors:
    def __init__(self, quant=COLOR_QUANTIZE):
        self.dictionary = {}
        self._quantize = quant

    def __len__(self):
        return len(self.dictionary)

    def _quant(self, color):
        return tuple(map(lambda n: int(math.floor(n / self._quantize) * self._quantize), color))

    def totalWeight(self):
        return sum(self.dictionary.values())

    def add(self, color, weight):
        # add to dictionary        default if not in dict --v
        self.dictionary[color] = self.dictionary.get(color, 0.0) + weight

    def addDict(self, colors, frac=1.0):
        for color, weight in colors.dictionary.items():
            self.add(color, weight * frac)

    def addImage(self, filename, frac=1.0):
        with Image.open(filename) as i:
            # Get opaque pixels (alpha >= 192) and add to colors weighted according to 
            colors = i.getcolors(1000000)

            # If a palette is defined, we need to connect colors in palette to values in colors
            pal = i.getpalette()
            if pal:
                colors = [(n, (pal[c*3],pal[c*3+1],pal[c*3+2],255)) for n, c in colors]

            colors_list = [(n, c[:3]) for n, c in colors if c[3] >= 192]
            pixel_count = sum(n for n, _ in colors_list)
            for num, color in colors_list:
                # Add to dictionary weighted according to coverage
                self.add(self._quant(color), (float(num) * float(frac)) / float(pixel_count))

    def divide(self, divisor):
        for color in self.dictionary:
            self.dictionary[color] = self.dictionary[color] / divisor.dictionary[color]

    def sort(self):
        """Sort internal color dictionary by weight (ascending)"""
        self.dictionary = {k: v for k, v in sorted(self.dictionary.items(), key=lambda x: -x[1])}

    def quantize(self):
        for color in [*self.dictionary]:  # for each color in dictionary
            quant_color = self._quant(color)
            if quant_color != color:  # if quantized color is different
                # remove from dictionary and add weight to quantized color
                self.add(quant_color, self.dictionary.pop(color))
        # Sort
        self.sort() 

    def removeBelow(self, t=0.01):
        self.dictionary = {k: v for k, v in self.dictionary.items() if v > t}

    def removeFraction(self, frac=0.02):
        self.sort()
        frac = frac * self.totalWeight()
        # iprint(f'weight={self.totalWeight()}, len={len(self.dictionary)}')
        removed_weight = 0.0
        while removed_weight < frac:
            removed_weight += self.dictionary.popitem()[1]

    def removeBlack(self, min=8): # Exclude colors where all r,g,b are less than the minimum
        # if DEBUG: iprint(f'weight={self.totalWeight()}, len={len(self.dictionary)}')
        self.dictionary = {k: v for k, v in self.dictionary.items() if (k[0]>min or k[1]>min or k[2]>min)}

    def removeGray(self, min=8): # Exclude colors where all r,g,b are all very similar
        # if DEBUG: iprint(f'weight={self.totalWeight()}, len={len(self.dictionary)}')
        iprint(f'weight={self.totalWeight()}, len={len(self.dictionary)}')

        for c in [*self.dictionary]:  # for each color in dictionary
            if (abs(c[0]-c[1]) + abs(c[1]-c[2]) + abs(c[2]-c[0])) < min:  # if quantized color is different
                self.dictionary.pop(c)
        
        iprint(f'weight={self.totalWeight()}, len={len(self.dictionary)}')

    def show3d(self):
        d = self.dictionary
        plt.style.use('dark_background')
        # plt.suptitle('Colors', color='#1e1e1e')
        # print(plt.style.available)
        ks = d.keys()

        ss = [d[k]**(1.0/3.0) for k in ks]
        ss = [(0.9*s/max(ss))+0.1 for s in ss] #Normalize
        cs = [(min((c[0])/256.0,1.0), min((c[1])/256.0,1.0), min((c[2])/256.0,1.0), min(s,1.0)) for c, s in zip(ks, ss)]
        rs = [c[0] for c in cs]
        gs = [c[1] for c in cs]
        bs = [c[2] for c in cs]
        ss = [(s*100.0*COLOR_QUANTIZE)+10.0 for s in ss] # bigger

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(rs, gs, bs, s=ss, c=cs, marker='.') #s=ss, 

        # Formatting
        ax.set_xlabel('Red')
        ax.set_ylabel('Green')
        ax.set_zlabel('Blue')
        # fig.set_facecolor('dimgray') ##1e1e1e
        # ax.set_facecolor('dimgray') ##1e1e1e
        fig.set_facecolor('#1e1e1e')
        ax.set_facecolor('#1e1e1e')
        ax.grid(False)
        ax.w_xaxis.pane.fill = False
        ax.w_yaxis.pane.fill = False
        ax.w_zaxis.pane.fill = False

        # Bonus: To get rid of the grid as well:
        # ax.grid(False)
        plt.show()




 ######  ##     ##    ###    ########  ########
##    ## ##     ##   ## ##   ##     ##    ##
##       ##     ##  ##   ##  ##     ##    ##
##       ######### ##     ## ########     ##
##       ##     ## ######### ##   ##      ##
##    ## ##     ## ##     ## ##    ##     ##
 ######  ##     ## ##     ## ##     ##    ##

def getColorArray(pair_sets, size=360):
    """Return a numpy array of length `size` where each value is the color of that angle of the circle cooresponding to `pair_sets`."""
    sets = len(pair_sets)
    big_array = np.zeros(shape=(sets, size, 3), dtype=np.uint32)
    # for each row...
    for i in range(sets):
        pairs = pair_sets[i]

        array = np.zeros(shape=(size, 3), dtype=np.uint32)
        # mult = float(size)/sum(w for c, w in pairs)
        mult = size / sum(w for c, w in pairs)
        angle = 0.0
        # for each color in the row...
        for pair in pairs:
            last = angle
            angle += pair[1] * mult
            rep = int(round(angle)) - int(last)
            color = np.reshape(np.array(pair[0], np.uint32), (1, 3))
            repeat = np.repeat(color, rep, 0)
            array[int(last):int(round(angle)), 0:3] = repeat
        big_array[i] = array
    return big_array

def npDiff(a, b):
    """Find the absolute square difference between two numpy arrays, `a` and `b`"""
    return np.sum(np.ravel(np.square(np.subtract(a, b))))

def npRoll(array, shift=1, axis=0):
    """Shift numpy array, `array`, to 'rotate' color wheel by `shift` entries"""
    return np.roll(array, shift, axis)

def nextRow(sets, angle_steps=1, size=360):
    # get array of just this row and the previous
    array = getColorArray(sets)

    # calculate base score which is the same for this permutation
    # mult = float(size) / 10.0
    mult = float(size) / 16.0
    base_score = mult * npDiff(array[1], npRoll(array[1]))  # difference to get distance within row

    best_score = FLOAT_MAX
    best_permutation = []
    best_angle = 0
    # for each possible angle of this row...
    for a in range(0, 360, angle_steps):
        # get score for this permutation, angle combo
        score = base_score
        score += npDiff(array[0], array[1])

        # check if it's the best score we've found
        if score < best_score:
            best_score = score
            best_permutation = sets[1]  # best permutation of new line
            best_angle = a

        # roll this array row for next iteration
        array[1] = npRoll(array[1], angle_steps)

    return best_permutation, best_score, best_angle

class Chart(Colors):
    @timed
    def _group(self, k):
        # copy arrays
        color_array = []
        weight_array = []
        for color, num in self.dictionary.items():
            color_array.append(color)
            weight_array.append(num)
        # do clustering
        #https://scikit-learn.org/stable/auto_examples/cluster/plot_cluster_comparison.html#sphx-glr-auto-examples-cluster-plot-cluster-comparison-py

        best_inertia = FLOAT_MAX
        best_algo = ""

        km1 = cluster.KMeans(n_clusters=k, init='k-means++', n_init=2, max_iter=300, tol=1e-4)
        km2 = cluster.KMeans(n_clusters=k, init='k-means++', n_init=10, max_iter=300, tol=1e-4)
        km3 = cluster.KMeans(n_clusters=k, init='k-means++', n_init=50, max_iter=300, tol=1e-4)
        km4 = cluster.KMeans(n_clusters=k, init='k-means++', n_init=250, max_iter=300, tol=1e-4)
        km5 = cluster.KMeans(n_clusters=k, init='k-means++', n_init=1250, max_iter=300, tol=1e-4)
        mbkm1 = cluster.MiniBatchKMeans(n_clusters=k, init='k-means++', n_init=3, max_iter=100, batch_size=1024, tol=0.0)
        mbkm2 = cluster.MiniBatchKMeans(n_clusters=k, init='k-means++', n_init=3, max_iter=100, batch_size=1024, tol=1e-3)
        mbkm3 = cluster.MiniBatchKMeans(n_clusters=k, init='k-means++', n_init=3, max_iter=100, batch_size=1024, tol=1e-4)
        mbkm4 = cluster.MiniBatchKMeans(n_clusters=k, init='k-means++', n_init=3, max_iter=100, batch_size=1024, tol=1e-5)
        mbkm5 = cluster.MiniBatchKMeans(n_clusters=k, init='k-means++', n_init=3, max_iter=100, batch_size=1024, tol=1e-6)
        
        algos = [
            # ("KMeans1", km1),
            # ("KMeans2", km2),
            # ("KMeans3", km3),
            # ("KMeans4", km4),
            # ("KMeans5", km5),
            ("MiniBatchKMeans1", mbkm1),
            # ("MiniBatchKMeans2", mbkm2),
            # ("MiniBatchKMeans3", mbkm3),
            # ("MiniBatchKMeans4", mbkm4),
            # ("MiniBatchKMeans5", mbkm5),
        ]

        fits = {}

        for name, algo in algos:
            # print('algo: '+name)
            fits[name] = algo.fit(color_array, None, weight_array)
            if fits[name].inertia_ < best_inertia:
                best_inertia = fits[name].inertia_
                best_algo = name
        
        fit = fits[best_algo]
        # print(f'Winner: {best_algo}, Inertia: {fit.inertia_:.2}, Iter: {fit.n_iter_}/{300}')

        fit_c = fit.cluster_centers_
        fit_l = fit.labels_
        counts = np.bincount(fit_l[fit_l >= 0])
        labels = np.argsort(-counts)

        # create color weight pairs
        pairs = []
        for label in labels:
            color = tuple(map(int, fit_c[label]))
            size = counts[label]
            pairs.append((color, size))

        # if DEBUG: iprint(f"Grouped {len(self.dictionary)} points on iter {fit.n_iter_}/{max_iter} with {fit.n_steps_} steps: {pairs}")
        # if DEBUG: iprint(f"Grouped {len(self.dictionary)} points on iter {fit.n_iter_}/{max_iter}: {pairs}")

        return pairs

    @timed
    def _permuteMulti(self, processes=8):
        # try all possible permutations and angles of each
        pool = mp.Pool(processes)

        for i, _ in enumerate(self.sets):
            # perms = list(it.permutations(self.sets[i]))
            perms = list(unique_cyclic_permutations(self.sets[i],len(self.sets[i])))

            if DEBUG: iprint(f"Checking {len(perms)} permutations at row {i} with {processes} processes")
            tasks = zip(it.repeat(self.sets[i - 1]), perms)
            bests = pool.map(nextRow, tasks)

            best_score = FLOAT_MAX
            best_permutation = []
            best_angle = 0
            for permutation, score, angle in bests:
                if score < best_score:
                    best_score = score
                    best_permutation = permutation
                    best_angle = angle

            self.sets[i] = best_permutation
            self.start_angles[i] = (best_angle + self.start_angles[i - 1]) % 360
        if DEBUG: iprint(f"angles = {self.start_angles}")
        pool.close()

    # @timed
    def _image(self, output_size):
        sets = len(self.sets)
        # sizes of each circle
        draw_size = output_size * CHART_SUPERSAMPLE

        cent = 1.0
        # if center is 1 solid color, make the circle a bit smaller
        if (len(self.sets[0]) == 1):
            cent = 0.8
        total_size = float(sets) - 1.0 + cent
        sizes = [(cent / total_size) * draw_size]  # first size
        for i in range(1, sets):
                sizes.append(draw_size * ((cent + i) / total_size))

        img = Image.new('RGBA', (draw_size, draw_size), COLOR_TRANSPARENT)
        draw = ImageDraw.Draw(img)
        for size, pairs, start_angle in zip(reversed(sizes), reversed(self.sets), reversed(self.start_angles)):
            tl = int((draw_size - size) / 2)
            box = (tl, tl, tl + size, tl + size)
            total_weight = sum(w for c, w in pairs)

            # draw slices
            degree = float(start_angle)
            for pair in pairs:
                start = degree
                degree += pair[1] * 360.0 / total_weight
                draw.pieslice(box, start, degree, pair[0], pair[0])

        del draw
        # resize to correct size and return
        img.thumbnail((output_size, output_size))
        return img

    def generate(self, ks=CHART_KS, size=CHART_SIZE):
        self.sets = []
        for k in ks:
            self.sets.append(self._group(k))
        self.start_angles = list(it.repeat(315, len(self.sets)))
        self._permuteMulti(CORES)
        return self._image(size)

    @timed
    def save(self, filename, ks=CHART_KS, size=CHART_SIZE, forced=False, quiet=False):
        if exists(filename) and not forced:
            if not quiet:
                print(f'{filename} already exists')
        else:
            if not quiet:
                img = time_print(self.generate,f'{filename} saving... ',ks=ks,size=size)
                img.save(filename)
            else:
                img = self.generate(ks=ks,size=size)
                img.save(filename)

        if DEBUG: 
            print('')