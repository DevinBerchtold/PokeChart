from pokemon import *

SAVE_POKES = True
SAVE_POKES_FORCED = True
SAVE_TYPES = True
SAVE_SHEET = True

# Pokemon numbers to process
POKEMON_GENERATIONS = {
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
FIRST_POKEMON, LAST_POKEMON = POKEMON_GENERATIONS[0]
POKEMON_NUMBERS = range(FIRST_POKEMON, LAST_POKEMON + 1)

# List of only Pokemon starters
POKEMON_STARTERS = []
for x in [1, 152, 252, 387, 495, 650, 722, 810]:
    POKEMON_STARTERS += range(x, x + 9)
POKEMON_NUMBERS = POKEMON_STARTERS

INDIVIDUAL_KS = (1, 3, 5) # 7.047s
# INDIVIDUAL_KS = (2, 4, 6) # 8.380s
# INDIVIDUAL_KS = (3, 5, 7)
# INDIVIDUAL_KS = (1, 2, 4, 6)
# v-- All these are SLOW --v
# INDIVIDUAL_KS = (1, 3, 5, 7) # 11.820s
# INDIVIDUAL_KS = (2, 4, 6, 8) # 23s
# INDIVIDUAL_KS = (1, 3, 5, 7, 9) # 97.064s
# INDIVIDUAL_KS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) # 829.580s
# INDIVIDUAL_KS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11) # 14581.832s

KS_STRING = ''
for k in INDIVIDUAL_KS:
    KS_STRING += str(k)

# GROUP_KS = (3, 5, 7, 9)
# GROUP_KS = (2, 4, 6, 8)
GROUP_KS = (1, 3, 5, 7)

GROUP_THRESHOLD = 0.10
GROUP_CHART_SIZE = CHART_SIZE * 4

# GROUP_FILENAME = f'_{PREFIX_STRING}_n{FIRST_POKEMON}-{LAST_POKEMON}_t{GROUP_THRESHOLD*100}.png'
# INDIVIDUAL_FILENAME = f'_k{KS_STRING}_{PREFIX_STRING}r{COLOR_REMOVE:02}_q{COLOR_QUANTIZE:02}.png'

INDIVIDUAL_CHART_SIZE = CHART_SIZE

INDIVIDUAL_PREFIX = 'art/art_'
INDIVIDUAL_FILENAME = f'_image.png'

GROUP_PREFIX = 'output/image_type_'
GROUP_FILENAME = '.png'

# TODO: Use this
def image_grid(imgs, rows, cols):
    assert len(imgs) == rows*cols

    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols*w, rows*h))
    grid_w, grid_h = grid.size
    
    for i, img in enumerate(imgs):
        grid.paste(img, box=(i%cols*w, i//cols*h))
    return grid

if __name__ == '__main__':
    if DEBUG: print('== D E B U G   O N ==\n')

    print('- Input -')

    # build pokemon data structures
    pokes = []
    for i in POKEMON_NUMBERS:
        # p = Pokemon(i)
        p = time_print(Pokemon,f'Loading Pokemon #{i}... ',i)
        pokes.append(p)

    # normalize type colors
    # for t in POKEMON_TYPES:
    #     if Pokemon.type_charts[t]:
    #         Pokemon.type_charts[t].divide(Pokemon.all_colors)

    print('\n- Output -')
    # output individual pokemon charts
    if SAVE_POKES:
        t0 = time.time()
        for p in pokes:
            p.chart.save(INDIVIDUAL_PREFIX+p.string+INDIVIDUAL_FILENAME,size=INDIVIDUAL_CHART_SIZE,ks=INDIVIDUAL_KS,forced=SAVE_POKES_FORCED)
        total = time.time()-t0
        print(f'Saved {len(pokes)} charts in {total:.3f}s ({total/len(pokes):.3f}s each)')

    # create group output images
    if SAVE_TYPES:
        for t in POKEMON_TYPES:
            # Pokemon.type_charts[t].removeBelow(GROUP_THRESHOLD)

            n = len(Pokemon.type_charts[t])
            if n > 10:
                filename = GROUP_PREFIX + t + GROUP_FILENAME
                Pokemon.type_charts[t].save(filename,size=GROUP_CHART_SIZE,ks=GROUP_KS,forced=True)

    if SAVE_SHEET:
        for t in POKEMON_TYPES:
            num = len(Pokemon.type_groups[t])
            if num > 1:
                space = 1.28
                center = True

                if center:
                    n = 5  # number of extra circles each row
                    # n = 6  # number of extra circles each row
                    m = 9  # number of circles in the first row
                    start_radius = 0.5
                else:
                    n = 6  # number of extra circles each row
                    m = 3  # number of circles in the first row
                    start_radius = -0.4

                # calculate number of rows in final pic
                sub = m
                rows = 1
                while num > sub:
                    num -= sub
                    rows += 1
                    sub += n

                size = CHART_SIZE/2
                width = int(space * 2.15 * size * (0.5 + rows))
                cent = (width - size) / 2
                sheet = Image.new('RGBA', (width, width), COLOR_TRANSPARENT)
                # Pokemon.type_groups[t].sort(key=lambda x: x.type_relations[t], reverse=True)

                # add the center (aggregated) circle
                if center:
                    cent_file = GROUP_PREFIX + t + GROUP_FILENAME
                    cent_image = Image.open(cent_file)
                    cent_size = size * 2.4
                    cent_image.thumbnail((cent_size, cent_size))
                    cent_pos = int((width - cent_size) / 2)
                    sheet.paste(cent_image, (cent_pos, cent_pos), cent_image)
                # else:
                #     cent_size = size * 8.0  # huge
                r = 1
                a_step = 360.0 / m
                a_offset = (a_step/2.0)
                a = 0.0
                num_left = len(Pokemon.type_groups[t])
                for p in Pokemon.type_groups[t]:
                    rad = (a+a_offset) * (math.pi / 180.0)
                    grow = 1.28

                    magnitude = size * (start_radius + r) * space
                    x = int((width/2.0) + (math.cos(rad) * magnitude))
                    y = int((width/2.0) + (math.sin(rad) * magnitude))

                    image = Image.open(p.chartname)
                    size_g = float(size)*grow
                    image.thumbnail((size_g, size_g))
                    offset = int(size_g/2.0)
                    sheet.paste(image, (x-offset, y-offset), image)

                    image = Image.open(p.filename)
                    image.thumbnail((size, size))
                    offset = int(size/2.0)
                    sheet.paste(image, (x-offset, y-offset), image)
                    num_left -= 1

                    # print(f'{p.filename} at {a} degrees')
                    a += a_step
                    if (a >= 359.0):
                        space = space + 0.05

                        r = r + 1
                        x = m + ((r-1) * n)  # number of circles in the next row
                        if x > num_left:
                            x = num_left
                        if x > 0:
                            a_step = 360.0 / x
                            a_offset += (a_step/2.0)
                        a = 0.0

                filename = f'output/image_circle_{t}.png'
                time_print(sheet.save,f'{filename} saving... ',filename)

    for p in pokes:
        del p