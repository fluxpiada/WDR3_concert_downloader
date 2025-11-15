#!/usr/bin/env python3

"""
Downloads mp3 files from a site where the WDR3 concert player is located if
there's only an afterhearing option of 30 days and, hence, no download button
available. Copy the url of the site, where the concert resides and run the code:

$ python3 WDR3_concert_downloader [-h] [-o <file>.mp3] <url>

where e.g.
url = https://www1.wdr.de/radio/wdr3/programm/sendungen/wdr3-konzert/konzertplayer-klassik-tage-alter-musik-in-herne-concerto-romano-alessandro-quarta-100.html
Note: if there are multiple mp3 media objects available on the provided website,
the files downloaded are named in following order:
file.mp3, file(1).mp3, file(2).mp3, etc. according to the objects encountered in
the html soup scan.
"""

import importlib.util
import os.path
import re
from argparse import ArgumentParser
from sys import exit
from typing import Annotated

from pydantic import BaseModel, ValidationError, StringConstraints

if importlib.util.find_spec("js2py_") is not None \
        and os.path.isfile("{}/concert_downloader_js.py".format(
    os.path.dirname(os.path.realpath(__file__)))
):
    from concert_downloader_js import wdr3_scraper
else:
    from concert_downloader1 import wdr3_scraper

__author__ = "Dr. Ralf Antonius Timmermann"
__copyright__ = ("Copyright (c) 2024-25, Dr. Ralf Antonius Timmermann "
                 "All rights reserved.")
__credits__ = []
__license__ = "BSD 3-Clause"
__version__ = "2.7.0"
__maintainer__ = "Dr. Ralf Antonius Timmermann"
__email__ = "ralf.timmermann@gmx.de"
__status__ = "Prod"

WDR3_URL_PATTERN = re.compile(r"https://www1\.wdr\.de/radio/wdr3(.)*$")


class TestURL(BaseModel):
    url: Annotated[str, StringConstraints(pattern=WDR3_URL_PATTERN)]


def checks(
        url: str,
        filepath: str = "download.mp3"
) -> None:
    """
    performs verious checks on url and file format and existance
    :param url: url string
    :param filepath: total file path
    :return: None
    """
    try:
        TestURL(url=url)
        if not os.path.splitext(filepath)[1][1:] == "mp3":
            raise NameError(filepath)
        dirname = os.path.dirname(filepath)
        if not dirname: dirname = '.'
        regex = re.compile(
            r"{}(\(\d\))?.mp3".format(
                os.path.splitext(os.path.basename(filepath))[0]
            )
        )
        if [file for file in os.listdir(dirname) if regex.match(file)]:
            raise FileExistsError(filepath)

        return

    except ValidationError as e:
        print("Error: {0} - {1} does not match pattern {2}".format(
            repr(e.errors()[0]['type']),
            url,
            WDR3_URL_PATTERN.pattern
        ))
    except NameError as e:
        print("Error: download filename '{}' is incorrect.".format(e))
    except FileExistsError as e:
        print("Error: download file '{}' exists. Exiting ...".format(e))

    exit(1)


def main() -> None:
    parser = ArgumentParser(
        description="Downloads audio mp3 files from WDR3 concert web sites.")
    parser.add_argument(
        '-o',
        '--output',
        default='download.mp3',
        nargs='?',
        help='Output file (.mp3) (default: download.mp3)')
    parser.add_argument('url',
                        help='URL of web site where concert player resides')

    pargs = parser.parse_args()

    checks(
        url=pargs.url,
        filepath=pargs.output
    )

    exit(
        wdr3_scraper(
            url=pargs.url,
            filepath=pargs.output
        )
    )


if __name__ == '__main__':
    main()
