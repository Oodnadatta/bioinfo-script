#! /bin/sh

if [ $# -ne 2 ]; then
    echo "Usage: $(basename $0) input.lst output.lst" >&2
    exit 1
fi

if ! sort -c "$1"; then
    echo "$1 is not sorted" >&2
    exit 1
fi

comm -1 -2 ~/db/genesdi.lst "$1" > "$2"
