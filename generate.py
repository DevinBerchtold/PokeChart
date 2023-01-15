from pokemon import *
from PIL import ImageEnhance
from PIL import ImageFilter



 ######   #######  ##    ##  ######  ########    ###    ##    ## ########  ######
##    ## ##     ## ###   ## ##    ##    ##      ## ##   ###   ##    ##    ##    ##
##       ##     ## ####  ## ##          ##     ##   ##  ####  ##    ##    ##
##       ##     ## ## ## ##  ######     ##    ##     ## ## ## ##    ##     ######
##       ##     ## ##  ####       ##    ##    ######### ##  ####    ##          ##
##    ## ##     ## ##   ### ##    ##    ##    ##     ## ##   ###    ##    ##    ##
 ######   #######  ##    ##  ######     ##    ##     ## ##    ##    ##     ######

SAVE_POKES = True
SAVE_POKES_FORCED = False
SAVE_TYPES = True
SAVE_TYPES_FORCED = False
SAVE_SHEET = True

# INDIVIDUAL_KS = (1, 3, 5) # 7.047s *
# INDIVIDUAL_KS = (2, 4, 6) # 8.380s *
INDIVIDUAL_KS = (1, 3, 5, 7) # 3.761s
# INDIVIDUAL_KS = (1, 2, 4, 6)
# v-- All these are SLOW --v
# INDIVIDUAL_KS = (1, 3, 5, 7) # 11.820s *
# INDIVIDUAL_KS = (2, 4, 6, 8) # 23s *
# INDIVIDUAL_KS = (1, 3, 5, 7, 9) # 97.064s *
# INDIVIDUAL_KS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) # 829.580s *
# INDIVIDUAL_KS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11) # 14581.832s *

KS_STRING = ''
for k in INDIVIDUAL_KS:
    KS_STRING += str(k)

# GROUP_KS = (3, 5, 7, 9)
# GROUP_KS = (2, 4, 6, 8)
GROUP_KS = (1, 2, 4, 6, 8, 10)

GROUP_THRESHOLD = 0.10
GROUP_CHART_SIZE = CHART_SIZE * 4

INDIVIDUAL_CHART_SIZE = CHART_SIZE

INDIVIDUAL_PREFIX = 'art/art_'
INDIVIDUAL_FILENAME = f'_image.png'

GROUP_PREFIX = 'output/image_type_'
GROUP_FILENAME = '.png'



##     ##    ###    #### ##    ##
###   ###   ## ##    ##  ###   ##
#### ####  ##   ##   ##  ####  ##
## ### ## ##     ##  ##  ## ## ##
##     ## #########  ##  ##  ####
##     ## ##     ##  ##  ##   ###
##     ## ##     ## #### ##    ##

def paste_shadow(a, b):
    dark = ImageEnhance.Brightness(b).enhance(0.0)
    shadow = dark.filter(ImageFilter.GaussianBlur(10))
    return Image.alpha_composite(Image.alpha_composite(a, shadow), b)

if __name__ == '__main__':
    if DEBUG: print('== D E B U G   O N ==\n')
    args = Pokemon.get_args()

    print('- Input -')

    # build pokemon data structures
    pokes = []
    for i in args.numbers:
        # p = Pokemon(i)
        p = time_print(Pokemon,f'Loading Pokemon #{i}... ',i)
        pokes.append(p)

    # normalize type colors
    # for t in POKE_TYPES:
    #     if Pokemon.type_charts[t]:
    #         Pokemon.type_charts[t].divide(Pokemon.all_colors)

    print('\n- Output -')
    # output individual pokemon charts
    if SAVE_POKES:
        num = len(pokes)
        t0 = time.time()
        for p in pokes:
            p.chart.save(INDIVIDUAL_PREFIX+p.string+INDIVIDUAL_FILENAME,size=INDIVIDUAL_CHART_SIZE,ks=INDIVIDUAL_KS,forced=SAVE_POKES_FORCED)
        total_time = time.time()-t0
        print(f'Saved {num} charts in {total_time:.3f}s ({total_time/num:.3f}s each)')

        if len(Chart.algorithms) > 1: # if more than one algorithm...
            for algo in Chart.algorithms: # then print out statistics for each algorithm
                s = Chart.algorithms[algo]
                if 'wins' in s:
                    print(f"{algo+':':<9} i:{s['inertia']/num:<7g} t:{s['time']/num:<8g} it:{s['inertia_time']/num:<7g} n:{s['iter']/num:<7g} w:{s['wins']}")
                else:
                    print(f"{algo+':':<9} i:{s['inertia']/num:<7g} t:{s['time']/num:<8g} it:{s['inertia_time']/num:<7g} n:{s['iter']/num:<7g}")

    # create group output images
    if SAVE_TYPES:
        for t in POKE_TYPES:
            # Pokemon.type_charts[t].removeBelow(GROUP_THRESHOLD)

            n = len(Pokemon.type_charts[t])
            if n > 10:
                filename = GROUP_PREFIX + t + GROUP_FILENAME
                Pokemon.type_charts[t].save(filename,size=GROUP_CHART_SIZE,ks=GROUP_KS,forced=SAVE_TYPES_FORCED)

    if SAVE_SHEET:
        for t in POKE_TYPES:
            num = len(Pokemon.type_groups[t])
            if num > 1:
                space = 2.0
                center = True

                if center:
                    # n = 5  # number of extra circles each row
                    # n = 6  # number of extra circles each row
                    # m = 9  # number of circles in the first row
                    # start_radius = 0.5
                    n = 6  # number of extra circles each row
                    m = 8  # number of circles in the first row
                    start_radius = 0.35
                    # n = 6  # number of extra circles each row
                    # m = 7  # number of circles in the first row
                    # start_radius = 0.20
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
                width = int(space * 2.07 * size * (1 + rows))
                cent = (width - size) / 2
                chart_scale = 2.0
                poke_scale = 1.40
                # cent_scale = 3.89
                cent_scale = 3.2
                
                pokes_sheet = Image.new('RGBA', (width, width), COLOR_TRANSPARENT)
                chart_sheet = Image.new('RGBA', (width, width), COLOR_TRANSPARENT)
                # Pokemon.type_groups[t].sort(key=lambda x: x.type_relations[t], reverse=True)

                # add the center (aggregated) circle
                if center:
                    cent_file = GROUP_PREFIX + t + GROUP_FILENAME
                    cent_image = Image.open(cent_file)
                    cent_size = size * cent_scale
                    cent_image.thumbnail((cent_size, cent_size))
                    cent_pos = int((width - cent_size) / 2)
                    chart_sheet.paste(cent_image, (cent_pos, cent_pos), cent_image)

                    icon_image = Image.open(f'image/icon_{t}.png')
                    # icon_size = cent_size * 0.40
                    icon_size = cent_size * 0.52
                    icon_image.thumbnail((icon_size, icon_size))
                    icon_pos = int((width - icon_size) / 2)
                    pokes_sheet.paste(icon_image, (icon_pos, icon_pos), icon_image)

                r = 1
                a_step = 360.0 / m
                a_offset = (a_step/2.0)
                a = 0.0
                num_left = len(Pokemon.type_groups[t])
                for p in Pokemon.type_groups[t]:
                    rad = (a+a_offset) * (math.pi / 180.0)

                    magnitude = size * (start_radius + r) * space
                    x = int((width/2.0) + (math.cos(rad) * magnitude))
                    y = int((width/2.0) + (math.sin(rad) * magnitude))

                    image = Image.open(p.chartname)
                    size_g = float(size)*chart_scale
                    image.thumbnail((size_g, size_g))
                    offset = int(size_g/2.0)
                    chart_sheet.paste(image, (x-offset, y-offset), image)

                    image = Image.open(p.filename)
                    size_g = float(size)*poke_scale
                    image.thumbnail((size_g, size_g))
                    offset = int(size_g/2.0)
                    pokes_sheet.paste(image, (x-offset, y-offset), image)
                    num_left -= 1

                    a += a_step
                    if (a >= 359.0):
                        space = space + 0.015

                        r = r + 1
                        x = m + ((r-1) * n)  # number of circles in the next row
                        if x > num_left:
                            x = num_left
                        if x > 0:
                            a_step = 360.0 / x
                            a_offset += (a_step/2.0)
                        a = 0.0

                # filename = f'output/image_type_{t}_chart.png' # Only Charts
                # time_print(chart_sheet.save,f'{filename} saving... ',filename)
                # filename = f'output/image_type_{t}_pokes.png' # Only Pokemon
                # time_print(pokes_sheet.save,f'{filename} saving... ',filename)

                pokes_dark = ImageEnhance.Brightness(pokes_sheet).enhance(0.0)
                pokes_shadow = pokes_dark.filter(ImageFilter.GaussianBlur(10))
                # filename = f'output/image_type_{t}_pokes_shadow.png' # Only Shadows
                # time_print(pokes_shadow.save,f'{filename} saving... ',filename)

                pokes_combined = Image.alpha_composite(Image.alpha_composite(chart_sheet, pokes_shadow), pokes_sheet)
                pokes_combined.thumbnail((width/4, width/4))
                filename = f'output/sheet_type_{t}_pokes.png' # Composite image
                time_print(pokes_combined.save,f'{filename} saving... ',filename)

    for p in pokes:
        del p