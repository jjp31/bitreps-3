from paths import INPUT_DIRECTORY, JSON_DIRECTORY
from bloom_filter2 import BloomFilter
from collections import defaultdict
from pathlib import Path
from tqdm import tqdm
import argparse
import json
import os

ALLOWED_BLOCKSIZES = [8, 16, 24, 32, 48, 64, 96, 128, 256, 512]     # All blocksizes supported (in bits)


def populate_bloom(blocks, err_rate, blocksize):
    """
    Create and populate Bloom filter based on user-specified parameters
    :param blocks: A list of all blocks in input data in integer form
    :param err_rate: Error rate of the Bloom filter (user-specified)
    :param blocksize: User-specified blocksize over which to perform measurements
    :return: Bloom filter populated with observed blocks, dictionary populated with block frequencies and metadata
    """
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

def get_blocks(fp, blocksize):
    """
    Gather and return all blocks in a file
    :param fp: Path to input file
    :param blocksize: User-specified size of collected blocks
    :return: A list of all blocks in the input data in integer form
    """
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
    """
    Obtain and validate user input, read input data, create Bloom filter and write repetition data to a JSON file
    :return: None
    """
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
