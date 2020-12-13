#! /usr/bin/env python3

#Anne-Sophie Denommé-Pichon
#AGPLv3

import sys

def upsample(upsampling_read_count, read_id):
    """
    upsampling_read_count : number of additional reads
    read_id : id of the read you want to repeat
    """
    try:
        max_lane = 0
        max_tile = 0
        max_x = 0
        max_y = 0
        while True: # boucle infinie pour lire les lignes 4 par 4
            title_line = next(sys.stdin).rstrip()
            sequence_line = next(sys.stdin).rstrip()
            plus_line = next(sys.stdin).rstrip()
            quality_line = next(sys.stdin).rstrip()
            print(title_line)
            print(sequence_line)
            print(plus_line)
            print(quality_line)
            
            lane = int(title_line.split(':')[2])
            if lane > max_lane:
                max_lane = lane
            
            tile = int(title_line.split(':')[3])
            if tile > max_tile:
                max_tile = tile
            
            x = int(title_line.split(':')[4])
            if x > max_x:
                max_x = x

            y = int(title_line.split(':')[5])
            if y > max_y:
                max_y = y

            if title_line == read_id:
                title_line_str = title_line
                sequence_line_str = sequence_line
                plus_line_str = plus_line
                quality_line_str = quality_line

    except StopIteration: # quand erreur StopIteration, arrêter
        pass
    
    for i in range(1, upsampling_read_count + 1):
        print(':'.join(title_line_str.split(':')[0:2] + [str(max_lane + i), str(max_tile + i), str(max_x + i), str(max_y + i)]))
        print(sequence_line_str)
        print('+')
        print(quality_line_str)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        upsample(int(sys.argv[1]), sys.argv[2])
    else:
        print("Usage: fastq_upsampling.py <upsampling_read_count> <read_id> < input.fastq > output.fastq", file=sys.stderr)
        sys.exit(1)
    
