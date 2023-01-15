Rem These are no longer necessary
Rem curl https://www.serebii.net/pokemon/art/[001-905].png -o "art/art_#1.png"
Rem curl https://www.serebii.net/swordshield/pokemon/[001-905].png -o "ss/ss_#1.png"
Rem curl https://www.serebii.net/pokedex-swsh/icon/[001-905].png -o "icon/icon_#1.png"
Rem "C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\magick.exe"
Rem Use these to make grids
magick montage -tile 9x0 -geometry 128x128+2+2 -background transparent art/art_%03d_image.png[001-151] output/gen_1.png
magick montage -tile 9x0 -geometry 128x128+2+2 -background transparent art/art_%03d_image.png[152-251] output/gen_2.png
magick montage -tile 9x0 -geometry 128x128+2+2 -background transparent art/art_%03d_image.png[252-386] output/gen_3.png
magick montage -tile 9x0 -geometry 128x128+2+2 -background transparent art/art_%03d_image.png[387-494] output/gen_4.png
magick montage -tile 9x0 -geometry 128x128+2+2 -background transparent art/art_%03d_image.png[495-649] output/gen_5.png
magick montage -tile 9x0 -geometry 128x128+2+2 -background transparent art/art_%03d_image.png[650-721] output/gen_6.png
magick montage -tile 9x0 -geometry 128x128+2+2 -background transparent art/art_%03d_image.png[722-809] output/gen_7.png
magick montage -tile 9x0 -geometry 128x128+2+2 -background transparent art/art_%03d_image.png[810-905] output/gen_8.png
magick montage -tile 9x0 -geometry 128x128+2+2 -background transparent art/art_%03d_image.png[906-1008] output/gen_9.png

Rem magick montage output/gen_%01d.png[1-9]  -tile 1x2  -geometry 128x128+2+2  miff:- |\
Rem     magick montage -  -geometry +0+0 -tile 8x1  output/all_gens_v.png

Rem magick montage output/gen_%01d.png[1-9]  -tile 1x3  -geometry 128x128+2+2  miff:- convert - +append output/all_gens_v.png

magick montage -tile 9x0 -geometry 128x128+2+2 -background transparent art/art_%03d_image.png[1-9] art/art_%03d_image.png[152-160] art/art_%03d_image.png[252-260] art/art_%03d_image.png[387-395] output/starters_4.png
magick montage -tile 9x0 -geometry 128x128+2+2 -background transparent art/art_%03d_image.png[1-9] art/art_%03d_image.png[152-160] art/art_%03d_image.png[252-260] art/art_%03d_image.png[387-395] art/art_%03d_image.png[495-503] art/art_%03d_image.png[650-658] art/art_%03d_image.png[722-730] art/art_%03d_image.png[810-818] art/art_%03d_image.png[906-914] output/starters_all.png
magick montage -tile 3x0 -geometry 1188x2376+16+16 -gravity North -background transparent output/gen_%01d.png[1-9] output/all_gens.png
Rem 1170x2340+8+8