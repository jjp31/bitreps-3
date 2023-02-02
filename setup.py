from paths import INPUT_DIRECTORY, JSON_DIRECTORY, OUTPUT_DIRECTORY
import os

if not os.path.isdir(INPUT_DIRECTORY):
    print("Creating directory: %s" % INPUT_DIRECTORY)
    os.mkdir(INPUT_DIRECTORY)
else:
    print("Directory: %s already exists!" % INPUT_DIRECTORY)

if not os.path.isdir(OUTPUT_DIRECTORY):
    print("Creating directory: %s" % OUTPUT_DIRECTORY)
    os.mkdir(OUTPUT_DIRECTORY)
else:
    print("Directory: %s already exists!" % OUTPUT_DIRECTORY)

if not os.path.isdir(JSON_DIRECTORY):
    print("Creating directory: %s" % JSON_DIRECTORY)
    os.mkdir(JSON_DIRECTORY)
else:
    print("Directory: %s already exists!" % JSON_DIRECTORY)
