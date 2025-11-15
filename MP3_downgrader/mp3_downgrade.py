#!/usr/bin/env python3

"""
Downgrade the quality of a mp3 input file to a smaller sized output file.
A mp3 input file is read and converted to a wav file stored temporily in memory,
subsequently converted again to a mp3 file by multiplying a factor <1
to the bit-rate.

We utilized a template provided by
https://github.com/miarec/pymp3
"""

import wave
from argparse import ArgumentParser
from io import BytesIO
from math import ceil
from os import path
from re import compile, findall
from typing import Generator

import mp3


class Range(object):
    def __init__(self, scope: str):
        b, f = r"([\[\]])", r"([-+]?(?:\d*\.\d+|\d+\.?)(?:[Ee][+-]?\d+)?)"
        r = compile(f'^{b} ?{f} ?, ?{f} ?{b}$')
        try: i = list(findall(r, scope)[0])
        except IndexError: raise SyntaxError("Range error!")
        if float(i[1]) >= float(i[2]): raise ArithmeticError("Range error!")
        self.__st = '{}{}, {}{}'.format(*i)
        i[0], i[-1] = {'[': '<=', ']': '<'}[i[0]], {']': '<=', '[': '<'}[i[-1]]
        self.__lambda = "lambda item: {1} {0} item {3} {2}".format(*i)
    def __eq__(self, item: float) -> bool: return eval(self.__lambda)(item)
    def __contains__(self, item: float) -> bool: return self.__eq__(item)
    def __iter__(self) -> Generator[object, None, None]: yield self
    def __str__(self) -> str: return self.__st
    def __repr__(self) -> str: return self.__str__()


class Validator(object):
    def __init__(self, pattern: str): self._pattern = compile(pattern)
    def __call__(self, value: str) -> str:
        if not self._pattern.match(value):
            print_error("Error: argument does not match RegEx '{}'"
                  .format(self._pattern.pattern))
        return value


def print_error(text: str) -> None:
    print("\033[91m{}\033[00m".format(text))
    exit(1)


def downgrade(
        *,
        factor: float,
        input_file: str,
        output_file: str
) -> int:
    memory_file = BytesIO()

    with (open(input_file, "rb") as read_file,
          wave.open(memory_file, 'wb') as wav_file):
        decoder = mp3.Decoder(read_file)

        sample_rate = decoder.get_sample_rate()
        nchannels = decoder.get_channels()
        bit_rate = decoder.get_bit_rate()
        print(
            f"Input file '{input_file}' parameter:\n"
            f"Number of channels: {nchannels}\n"
            f"Sample rate: {sample_rate} samples/second\n"
            f"Bit rate: {bit_rate} kb/second\n"
            f"Layer: {decoder.get_layer()}\n"
            f"Mode: {decoder.get_mode()}\n"
        )
        wav_file.setnchannels(nchannels)
        # Only PCM 16-bit sample size is supported for reconversion to mp3
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        while True:
             pcm_data = decoder.read(4000)
             if not pcm_data:
                 break
             else:
                 wav_file.writeframes(pcm_data)

    print("Writing to output file ...\n")
    memory_file.seek(0)

    with (open(output_file, "wb") as write_file,
          wave.open(memory_file) as wav_file):
        encoder = mp3.Encoder(write_file)

        frame_rate = wav_file.getframerate()
        nchannels = wav_file.getnchannels()
        bit_rate: int = ceil(bit_rate * factor)  # must be integer

        encoder.set_bit_rate(bit_rate)
        encoder.set_sample_rate(frame_rate)
        encoder.set_channels(nchannels)
        encoder.set_quality(2)   # 2-highest, 7-fastest
        encoder.set_mode(
            mp3.MODE_STEREO if nchannels == 2 else mp3.MODE_SINGLE_CHANNEL
        )
        while True:
            pcm_data = wav_file.readframes(8000)
            if pcm_data:
                encoder.write(pcm_data)
            else:
                encoder.flush()
                break
        print(
            f"Output file '{output_file}' parameter:\n"
            f"Number of channels: {nchannels}\n"
            f"Frame rate: {frame_rate} samples/second\n"
            f"Bit rate: {bit_rate} kb/second\n"
            f"Mode: {mp3.MODE_STEREO 
            if nchannels == 2 else mp3.MODE_SINGLE_CHANNEL}"
        )

    return 0


def main() -> None:
    mp3_validator = Validator(r"^.+\.mp3$")
    parser = ArgumentParser(
        description="Downgrades audio mp3 files from WDR3 concert web sites.")
    parser.add_argument(
        '-f',
        '--factor',
        required=True,
        help='Downgrade factor',
        type=float,
        choices=Range('[0.1, 1[')
    )
    parser.add_argument(
        '-i',
        '--input',
        required=True,
        type=mp3_validator,
        help='Input file (.mp3)')
    parser.add_argument(
        '-o',
        '--output',
        type=mp3_validator,
        nargs='?',
        help='Output file (.mp3) (default=<input_file>_down.mp3)')

    input_file = parser.parse_args().input
    if not path.isfile(input_file):
        print_error("Error: input file '{}' does not exist.".format(input_file))
    if parser.parse_args().output is None:
        output_file = path.splitext(input_file)[0] + "_down.mp3"
    else:
        output_file = parser.parse_args().output
        if output_file == input_file:
            print_error("Error: output file equals input file.")

    exit(
        downgrade(
            factor=parser.parse_args().factor,
            input_file=input_file,
            output_file=output_file
        ))
