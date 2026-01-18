# pycamo
A rudimentary camouflage generator in python.

## Prerequisites
- Python3
- Enough free space to generate between 1mb and 5mb images

## Installation
Installation is straightforward: Navigate to the directory, instantiate a virtual environment, activate said env, install the requirements, run the program.

```
	cd ~/pycamo
	python3 -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt
	python camo.py
```

Running this script will output 3 distinct images in a preset color palette in an organic pattern.

## Patterns, Colors, Params
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