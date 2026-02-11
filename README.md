# pycamo
A rudimentary camouflage generator in python.

## Prerequisites
- Python3
- Enough free space to generate between 1mb and 5mb images

## Installation
Navigate to the directory, instantiate a virtual environment, activate said env, install the requirements, run the program.

```bash
cd ~/pycamo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python camo.py
```

Running this script will output 3 distinct images in a preset color palette in an organic pattern.

## Patterns
There are a vairety of patterns supported, each taking inspiration from a variety of camouflage types.

### Organic (default)
The default camouflage pattern type. A woodland-type camouflage, using organic, rounded shapes.
![Organic in "clay" preset palette](output/camo_1dd77f17.png)

`python camo.py`
`python camo.py --type organic --preset clay`

### Chunk
Inspired by the M90 and other splinter-type camouflage patterns, this uses a similar layout to organic, but with less rounded edges and more straight lines.
![Chunk in "concrete" preset palette](output/camo_b2bd3b48.png)

`python camo.py --type chunk --preset concrete`

### Brush
A brushstroke-ish pattern somewhere between a traditional brushstroke and tiger striped camouflage.
![Brush in "piedmont" preset palette](output/camo_a17551f5.png)

`python camo.py --type brush`

### Jagged
An avant-garde, harsh camo pattern. An attempt to make a pattern that would be in deep ruffiage or, if the correct color palette applied, something like a winter camo.
![Jagged in a custom palette](output/camo_d7993c28.png)

`python camo.py --type jagged --colors #f2f2f2,#ebebeb,#e0e0e0,#dedede,#d9d9d9`

### Tiger
Inspired by Vietnam-era Tigerstripe. It generates horizontal, interlocking bands that warp and flow across the image.

![Tiger-inspired with the bergen palette](output/camo_58e5989f.png)

`python camo.py --type tiger --preset bergen --no_outline`

### KLMK (Digital)
Inspired by the Soviet "Berezka" (Birch Leaf) pattern. It uses a quantized noise algorithm to create a stair-step "digital" effect with jagged edges.

![KLMK with a custom 2-color palette](output/camo_klmk_klmk_6cb004b5.png)

`python camo.py --type klmk --colors #1C1C1C,#47503a`

## Colors
The application supports 6 predefined color palettes, and a potentially infinite number of additional colors.

### Preset
The preset palettes are `piedmont` (default), `clay`, `concrete`, `winterlock`, `bergen`, and `klmk`. These can be set using the `--preset` flag.

`python camo.py --preset concrete`
`python camo.py --preset winterlock`
`python camo.py --preset klmk`

### Custom
Camouflage can be generated using custom color palettes as well. Including a `--colors` param followed by a comma-delimited list of hex codes will generate a custom camouflage in the desired palette.

`python camo.py --colors #6A3B28,#4A5D44,#8C7B65`
`python camo.py --colors "#896E60,#95837A,#4E5B51"`
`python camo.py --type jagged --colors #f2f2f2,#ebebeb,#e0e0e0,#dedede,#d9d9d9`

## Modifiers
In addition to type and color palette, each camouflage can be modified with additional settings, each building on top of one another.

- `--limit` limit the nume of iterations. By default, 3 patterns are generated.
- `--no_outline` will remove the 20px outline around each shape, giving a flatter look.
- `--grid` will generate an occlusion grid, ideally designed to give computer-vision a harder time with organic shapes.
- `--grid_color` can be used as a modifier to also set a hex color for the grid. By default, it uses a very dark grey.
- `--rain` will add grid-colored streaks of "rain" to the image, imitating a Splittertarnmuster-type look
- `--modulation` will modulate each layer to give it a digital camouflage look to the color scheme

A complex pattern might look something like this:
`python camo.py --preset concrete --type jagged --grid --rain --modulation --no_outline`
![Generated jagged pattern, using a variety of modifiers](output/camo_b6ede47f.png)
