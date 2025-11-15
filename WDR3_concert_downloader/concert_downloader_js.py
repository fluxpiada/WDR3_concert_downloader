#!/usr/bin/env python3

"""
this is an alternative solution for the concert_download1.py module
see for conversion from JavaScript to Python 3.13
https://github.com/PiotrDabkowski/Js2Py
"""

import re

import js2py_  # ECMA 6 support is still experimental, check for final development
import requests
from bs4 import BeautifulSoup

PATTERN = re.compile(r'"audioURL"\s?:\s?"(.*\.mp3)"')
# Javascript definitions and supplements
JS_PREFIX = "var globalObject = {};\n"
JS_SUFFIX = (
    "var firstkey = Object.keys(globalObject.gseaInlineMediaData)[0];\n"
    "globalObject.gseaInlineMediaData[firstkey];\n"
)


def wdr3_scraper(
        url: str,
        filepath: str = "download.mp3"
) -> int:
    """
    download mp3(s)
    :param url:
    :param filepath:
    :return: exit code
    """
    counter = 0
    try:
        # verificare e tentare d'aprire url iniziale
        r = requests.get(url=url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # extract content within script tags which matches regEx
        for script in soup.find_all('script', text=PATTERN):
            # js_dict is js2py_.base.JsObjectWrapper, not dict, it's an object!
            js_dict = js2py_.eval_js(JS_PREFIX + script.string + JS_SUFFIX)
            mp3_url = js_dict['mediaResource']['dflt']['audioURL']

            if mp3_url:
                file_download = \
                    filepath if counter == 0 else "{0}_{1}.mp3".format(
                        filepath.rsplit(".", 1)[0],
                        counter
                    )
                sneak_mp3 = "https:{}".format(mp3_url)
                # apri l'oggetto mp3 e download suo contenuto binario sul file
                mp3 = requests.get(url=sneak_mp3)
                mp3.raise_for_status()
                with open(file_download, 'wb') as f:
                    f.write(mp3.content)
                print("{1} downloaded to {0} successfully".format(
                    file_download,
                    sneak_mp3
                ))
                counter += 1
        if counter == 0:
            raise RuntimeWarning

        return 0

    except RuntimeWarning:
        print("Warning: No mp3 link found under '{}' html.".format(url))
    except Exception as e:
        print("Error: {}".format(str(e)))  # Minchia, che palle!

    return 1
