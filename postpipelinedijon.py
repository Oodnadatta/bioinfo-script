#! /usr/bin/env python3

import sys

if len(sys.argv) != 2:
	print('Usage: postpipelinedijon.py filename', file=sys.stderr)
	sys.exit(1)
with open(sys.argv[1], 'r') as file:
	for line in file:
		print(line)
	
