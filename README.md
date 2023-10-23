<div align="center">
   <img src="https://s3.eu-north-1.amazonaws.com/dp2.dl/readme/es7s/holms/logo.png" width="96" height="96"><br>
   <img src="https://s3.eu-north-1.amazonaws.com/dp2.dl/readme/es7s/holms/label.png" width="200" height="64">
</div>

<div align="center">
  <img src="https://img.shields.io/badge/python-3.10-3776AB?logo=python&logoColor=white&labelColor=333333">
  <a href="https://pepy.tech/project/holms/"><img alt="Downloads" src="https://pepy.tech/badge/holms"></a>
  <br>
  <a href="https://pypi.org/project/holms/"><img alt="PyPI" src="https://img.shields.io/pypi/v/holms"></a>
  <a href='https://coveralls.io/github/es7s/holms?branch=master'><img src='https://coveralls.io/repos/github/es7s/holms/badge.svg?branch=master' alt='Coverage Status' /></a>
  <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</div>
<h1> </h1>

@ DESC


## Motivation

@ DESC


## Installation

    pipx install holms


## Basic usage

@ IMG

## Configuration / Advanced usage

    Usage: holms [OPTIONS] FILE
    
      Read data from FILE, find all valid UTF-8 byte sequences, decode them and display as separate Unicode code points.
      Use '-' as FILE to read from stdin instead.
    
    Options:
      -f, --format [offset|number|char|count|category|name]
                                      Comma-separated list of columns to show. The order of items determines the order of
                                      columns in the output. Default is to show all columns in the order specified above.
                                      Note that 'count' column is visible only when '-s' is specified. 'number' is the ID
                                      of code point (U+xxxx).
      -u, --unbuffered                Start streaming the result as soon as possible, do not read the whole input
                                      preemptively. See BUFFERING paragraph above for the details.
      -s, --squash                    Replace all sequences of repeating characters with the first character from each,
                                      followed by a length of the sequence.
      --decimal                       Use decimal offsets instead of hexadecimal.
      -V, --version                   Show the version and exit.
      --help                          Show this message and exit.

## Examples



## Buffering

The application works in two modes: buffered (the default) and unbuffered. 

In **buffered** mode the result begins to appear only after EOF is encountered. This is suitable for relatively short and predictable inputs (e.g. from a file) and allows to produce the most compact output (because all the column sizes are known from the start).

When input is not a file and can proceed infinitely (e.g. a piped stream), the **unbuffered** mode comes in handy: the application prints the results in real time, as soon as the type of each byte sequence is determined. 

> Despite the name, it actually uses a tiny input buffer (size is 4 bytes), but it's the only way to handle UTF-8 stream and distinguish valid sequences from broken ones; in truly unbuffered mode the output would consist of ASCII-7 characters (0x00-0x7F) and unrecogniesed binary data (0x80-0xFF) only, which is not something the application was made for.


## Changelog

@ WIP
