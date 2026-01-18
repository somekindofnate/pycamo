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
A woodland-type camouflage, using organic shapes.
![Organic in "clay" preset palette](output/camo_1dd77f17.png)