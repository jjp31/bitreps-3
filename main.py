from bloom_filter2 import BloomFilter
from collections import defaultdict
from pathlib import Path
from tqdm import tqdm
import argparse
import json
import os

ALLOWED_BLOCKSIZES = [8, 16, 24, 32, 48, 64, 96, 128, 256, 512]
INPUT_DIRECTORY = os.path.join(".", "input")
OUTPUT_DIRECTORY = os.path.join(".", "output")
JSON_DIRECTORY = os.path.join(".", "json")


def populate_bloom(blocks, err_rate, blocksize):
    # Prepare intermediary JSON
    reps = {
        "hits": defaultdict(lambda: 0),
        "blocksize": blocksize,
        "err_rate": err_rate,
        "num_blocks": len(blocks)
    }

    # Instantiate Bloom filter
    num_blocks = len(blocks)
    bf = BloomFilter(max_elements=num_blocks, error_rate=err_rate)

    # Populate Bloom filter and JSON
    for block in tqdm(blocks):
        if block not in bf:
            bf.add(block)
        else:
            reps["hits"][block] += 1
    return bf, reps


def dir_setup():
    # Create required directories if they do not already exist
    if not os.path.isdir(INPUT_DIRECTORY):
        os.mkdir(INPUT_DIRECTORY)
    if not os.path.isdir(OUTPUT_DIRECTORY):
        os.mkdir(OUTPUT_DIRECTORY)
    if not os.path.isdir(JSON_DIRECTORY):
        os.mkdir(JSON_DIRECTORY)


def get_blocks(fp, blocksize):
    blocks = []
    # Read file block by block until no blocks remain
    with open(fp, "rb") as f:
        while True:
            block = f.read(blocksize)
            if not block:
                break
            blocks.append(int.from_bytes(block, "big"))
    return blocks


def main():
    # Set up working directory
    dir_setup()

    # Get user input
    parser = argparse.ArgumentParser()
    parser.add_argument("fn", help="Name of file to measure")
    parser.add_argument("blocksize", help="Size of repetition to consider (in bits)")
    parser.add_argument("err_rate", help="Error rate of Bloom filter")
    args = parser.parse_args()

    fp = os.path.join(INPUT_DIRECTORY, args.fn)
    blocksize = int(args.blocksize)
    err_rate = float(args.err_rate)

    # Validate user input
    assert blocksize in ALLOWED_BLOCKSIZES
    assert os.path.exists(fp)
    assert 0 < err_rate < 1

    # Read file as raw data
    blocks = get_blocks(fp, int(blocksize / 8))

    # Create Bloom filter and populate it with blocks
    bf, reps = populate_bloom(blocks, err_rate, blocksize)

    # Write JSON
    with open(os.path.join(JSON_DIRECTORY, "%s-%s-%s.json" % (Path(fp).stem, blocksize, float(err_rate))), "w") as f:
        json.dump(reps, f, indent=2)


if __name__ == "__main__":
    main()
