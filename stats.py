from paths import JSON_DIRECTORY, OUTPUT_DIRECTORY
from scipy.stats import chisquare
from collections import Counter
from pathlib import Path
import argparse
import json
import os


def write_results(raw_exp_counts, raw_obs_counts, exp_counts, obs_counts, chisq, ddof, fn):
    """
    Write BitReps statistical output to a .txt file in ./output, using the following naming scheme:
    <INPUT-DATA-NAME>-<BLOCKSIZE>-<ERROR_RATE>.txt
    :return: None
    """
    s1 = "Unmodified expected distribution: %s\n" % raw_exp_counts
    s2 = "Unmodified observed distribution: %s\n\n" % raw_obs_counts
    s3 = "Expected distribution used for chi-square calculation: %s\n" % exp_counts
    s4 = "Observed distribution used for chi-square calculation: %s\n\n" % obs_counts
    s5 = "Chi-square: %s\n" % chisq[0]
    s6 = "P-Value: %s\n" % chisq[1]
    s7 = "Degrees of Freedom: %s" % ddof
    lines = [s1, s2, s3, s4, s5, s6, s7]
    with open(os.path.join(OUTPUT_DIRECTORY, "%s.txt" % Path(fn).stem), "w") as f:
        for line in lines:
            f.write(line)


def calc_chisq(obs, exp):
    """
    Use the Scipy chisquare() function to calculate statistic and p-value
    :param obs: List of observed frequencies
    :param exp: List of expected frequencies
    :return: Chi-square statistic and p-value
    """
    chisq = chisquare(obs, exp)
    return chisq


def fix_buckets(input, model):
    """
    Given the observed and expected distributions (represnted as Counter objects), remove extra buckets from the
    observed distribution and add in any buckets that are present in the expected, but not the observed, distribution
    :param input: Counter representing observed distribution
    :param model: Counter representing expected distribution
    :return: Dictionary representing updated observed distribution
    """
    new_input = {}
    for k, v in model.items():
        if k in input:
            new_input[k] = input[k]
        else:
            new_input[k] = 0
    return new_input


def remove_small_buckets(counts):
    """
    Given a distribution, remove all buckets with a frequency of less than 5
    :param counts: Dictionary representing distribution
    :return: Dictionary with small buckets removed
    """
    new_counts = {}
    for k, v in counts.items():
        if v > 4:
            new_counts[k] = v
    return new_counts


def get_repetition_distribution(data):
    """
    Given BitReps JSON, extract every occurrence frequency and append to a list
    :param data: BitReps JSON file represented as JSON object
    :return: List of occurrence frequencies
    """
    distribution = []
    for k, v in data["hits"].items():
        for i in range(v):
            distribution.append(v)
    return distribution


def add_uniques(data, num_blocks):
    """
    Append unique blocks to distribution
    :param data: List of block occurrences
    :param num_blocks: Total number of blocks in input data
    :return: List of block occurrences, including unique blocks
    """
    num_uniques = num_blocks - len(data)
    for i in range(num_uniques):
        data.append(1)
    return data

def read_json(fp):
    """
    Read JSON file into JSON object
    :param fp: File path of JSON file
    :return: JSON object
    """
    with open(fp, "r") as f:
        data = json.load(f)
    return data


def main():
    # Get user input
    parser = argparse.ArgumentParser()
    parser.add_argument("inf", help="Name of JSON file to analyse")
    parser.add_argument("mof", help="Name of model JSON file")
    args = parser.parse_args()

    infp = os.path.join(JSON_DIRECTORY, args.inf)
    mofp = os.path.join(JSON_DIRECTORY, args.mof)

    # Validate user input
    assert os.path.exists(infp)
    assert os.path.exists(mofp)

    # Read specified files into JSON objects
    input_json = read_json(infp)
    model_json = read_json(mofp)

    # Ensure that the input file and model file were measured using the same parameters
    assert input_json["blocksize"] == model_json["blocksize"]
    assert input_json["err_rate"] == model_json["err_rate"]
    assert input_json["num_blocks"] == model_json["num_blocks"]

    # PERFORM RATIO CALCULATIONS
    # Determine average error rate across life-span of Bloom filter
    # Use this to determine expected number of false positives
    # Use formula to determine expected number of genuine repetitions
    # Count number of hits in intermediary JSON
    # Print exp_fps, exp_reps, obs_reps, ratio
    pass

    # PERFORM CHI-SQUARE CALCULATIONS
    # Get list of repetition counts for input and model
    # List contains each frequency from JSON
    input_distribution = get_repetition_distribution(input_json)
    model_distribution = get_repetition_distribution(model_json)

    # Account for unique blocks
    # Previous lists get "1" appended for each missing block, up to total number of blocks
    input_distribution_full = add_uniques(input_distribution, input_json["num_blocks"])
    model_distribution_full = add_uniques(model_distribution, input_json["num_blocks"])

    # Count elements in input and model repetition counts
    # Results in dictionary that maps each frequency with the number of times it appears
    input_counts = Counter(input_distribution_full)
    model_counts = Counter(model_distribution_full)

    # Remove buckets with less than 5 elements from expected distribution
    # End result is a dictionary that is either the same as before, or smaller
    model_counts_trimmed = remove_small_buckets(model_counts)
    assert len(model_counts_trimmed) > 0

    # Remove extra buckets, pad non-existent buckets in observed distribution
    # This ensures buckets that do not exist within the expected distribution are disregarded, and expected buckets
    # that do not appear within the observed distribution are accounted for, ensuring chi-square validity
    input_counts_fixed = fix_buckets(input_counts, model_counts_trimmed)

    # Convert count objects into lists of frequencies for chi-square calculation
    # End result is lists containing extracted frequencies for each block repetition count. This is the expected
    # format for the chi-square calculation function in Scipy
    input_freqs = []
    model_freqs = []

    for k, v in sorted(input_counts_fixed.items()):
        input_freqs.append(v)
    for k, v in sorted(model_counts_trimmed.items()):
        model_freqs.append(v)

    # Perform chi-square calculation
    chisq = calc_chisq(input_freqs, model_freqs)
    ddof = len(model_counts_trimmed.items()) - 1

    # Print results to command line
    write_results(sorted(model_counts.items()),
                  sorted(input_counts.items()),
                  sorted(model_counts_trimmed.items()),
                  sorted(input_counts_fixed.items()),
                  chisq,
                  ddof,
                  args.inf)


if __name__ == "__main__":
    main()
