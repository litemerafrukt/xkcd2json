#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get cartoons from xkcd, build json.
Url to xkcd hardcoded.

Exit with 0 on success, 1 on fail
"""
import sys
import os
import getopt
import random
import base64
import json
import requests
from bs4 import BeautifulSoup

import traceback

EXIT_SUCCESS = 0
EXIT_FAIL = 1
MIN_RANDOM = 1
MAX_RANDOM = 1666
NR_OF_CARTOONS = 10
XKCD_BASE = 'http://xkcd.com/'

# Script info and usage
PROGRAM = os.path.basename(sys.argv[0])
AUTHOR = "4ny"
VERSION = "0.1a_debug"
USAGE = """{program}
By {author}
Version {version}

Usage:
  {program} [options] <output_image_file>

  This program builds a json file from some
  random xkcd cartons. Image are base64 encoded.

Options:
  -h, --help      display this help message.
  --low=<nr>      lowest xkcd to fetch, default {min}.
  --high=<nr>     highest xkcd to fetch, default {max}.
  --cartoons=<nr> nr of cartons to fetch, default {nr}.
""".format(program=PROGRAM, author=AUTHOR, version=VERSION, min=MIN_RANDOM, max=MAX_RANDOM, nr=NR_OF_CARTOONS)


def print_help(exit_status):
    """
    Print helptext and exit
    """
    print(USAGE)
    sys.exit(exit_status)


def main(argv):
    """
    Main function, parse arguments and do as told
    """

    global MIN_RANDOM, MAX_RANDOM, NR_OF_CARTOONS

    try:
        opts, args = getopt.getopt(argv, "h", ["help", "low=", "high=", "cartoons="])

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print_help(EXIT_SUCCESS)
            elif opt in "--low":
                MIN_RANDOM = int(arg)
            elif opt in "--high":
                MAX_RANDOM = int(arg)
            elif opt in "--cartoons":
                NR_OF_CARTOONS = int(arg)
            else:
                assert False, "Unhandled option"

        if len(args) != 1:
            print("No output file specified.")
            sys.exit(EXIT_FAIL)

        filename = args[0]

        json_out = {'info': 'From xkcd.com', 'cartoons': []}

        for _ in range(NR_OF_CARTOONS):
            # Randomize cartoon
            page_url = XKCD_BASE + str(random.randint(MIN_RANDOM, MAX_RANDOM))
            # Get page by requests
            resp_obj = requests.get(page_url)
            # Build soup
            soup = BeautifulSoup(resp_obj.text, "html.parser")
            # Find image url
            image_url = ''
            image_tags = soup.find_all("img")
            # print(image_tags)
            for image_tag in image_tags:
                image_url = image_tag.get('src')
                if 'comics' in image_url:
                    image_url = 'http:' + image_url
                    image_title = image_tag.get('title')

                    print(image_url)
                    print(image_title)

                    resp_obj = requests.get(image_url)
                    image_b64 = base64.b64encode(resp_obj.content)

                    i_obj = {'url': image_url, 'cartoon': image_b64, 'text': image_title}
                    json_out['cartoons'].append(i_obj)
                    break

        # Save json
        with open(filename, 'w') as fp:
            fp.write(json.dumps(json_out, ensure_ascii=True, indent=4, sort_keys=True))

    except Exception as err:
        print(err)
        # Prints the callstack, good for debugging, comment out for production
        traceback.print_exception(Exception, err, None)
        # print("\n---\n")
        # print_help(EXIT_FAIL)


if __name__ == "__main__":
    main(sys.argv[1:])
