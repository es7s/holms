<h1 align="center">
   <!-- es7s/holms -->
   <a href="##"><img align="left" src="https://s3.eu-north-1.amazonaws.com/dp2.dl/readme/es7s/holms/logo.png?v=2" width="160" height="64"></a>
   <a href="##"><img align="center" src="https://s3.eu-north-1.amazonaws.com/dp2.dl/readme/es7s/holms/label.png" width="200" height="64"></a>
   <a href="##"><img align="right" src="https://s3.eu-north-1.amazonaws.com/dp2.dl/readme/empty.png" width="160" height="64"></a>
</h1>
<div align="right">
 <a href="##"><img src="https://img.shields.io/badge/python-3.10-3776AB?logo=python&logoColor=white&labelColor=333333"></a>
 <a href="https://pepy.tech/project/holms/"><img alt="Downloads" src="https://pepy.tech/badge/holms"></a>
 <a href="https://pypi.org/project/holms/"><img alt="PyPI" src="https://img.shields.io/pypi/v/holms"></a>
 <a href='https://coveralls.io/github/es7s/holms?branch=master'><img src='https://coveralls.io/repos/github/es7s/holms/badge.svg?branch=master' alt='Coverage Status' /></a>
 <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
 <a href="##"><img src="https://wakatime.com/badge/user/8eb9e217-791b-436f-b729-81eb63e84b08/project/018b5923-4968-4029-ae8d-3776792f88d5.svg"></a>
</div>
<br>

CLI UTF-8 decomposer for text analysis capable of displaying Unicode code point
names and categories, along with ASCII control characters, UTF-16 surrogate pair
pieces, invalid UTF-8 sequences parts as separate bytes, etc.


Motivation
---------------------------

A necessity for a tool that can quickly identify otherwise indistinguishable
Unicode code points.


Installation
---------------------------
    pipx install holms


Basic usage
---------------------------

    Usage: holms run [OPTIONS] [INPUT]
    
      Read data from INPUT file, find all valid UTF-8 byte sequences, decode them and display as
      separate Unicode code points. Use '-' as INPUT to read from stdin instead.

<div align="center">
  <img alt="example001" width="49%" src="https://github.com/es7s/holms/assets/50381946/c3046efa-7192-4318-9fd9-056848bfaf82">
  <img alt="example004" width="49%" src="https://github.com/es7s/holms/assets/50381946/4acb7cb3-e97b-4c27-829e-c78907787cb2">
  <img alt="example002" width="49%" src="https://github.com/es7s/holms/assets/50381946/6ce86749-b628-4313-8e81-713f44f40650">
  <img alt="example003" width="49%" src="https://github.com/es7s/holms/assets/50381946/b33abedb-6d4a-47b6-93b5-e54e5a385ae7">
</div>

<details>
   <summary>Plain text output</summary>
   <!-- @sub:example001.png.txt -->

      > holms run  -u - <<<'1₂³⅘↉⏨'
    
      0  U+  31 ▕ 1 ▏ Nd DIGIT ONE
      1  U+2082 ▕ ₂ ▏ No SUBSCRIPT TWO
      4  U+  B3 ▕ ³ ▏ No SUPERSCRIPT THREE
      6  U+2158 ▕ ⅘ ▏ No VULGAR FRACTION FOUR FIFTHS
      9  U+2189 ▕ ↉ ▏ No VULGAR FRACTION ZERO THIRDS
      c  U+23E8 ▕ ⏨ ▏ So DECIMAL EXPONENT SYMBOL

   <!-- @sub -->
   <!-- @sub:example004.png.txt -->

      > holms run  -u - <<<'🌯👄🤡🎈🐳🐍'
    
      00  U1F32F ▕🌯 ▏ So BURRITO
      04  U1F444 ▕👄 ▏ So MOUTH
      08  U1F921 ▕🤡 ▏ So CLOWN FACE
      0c  U1F388 ▕🎈 ▏ So BALLOON
      10  U1F433 ▕🐳 ▏ So SPOUTING WHALE
      14  U1F40D ▕🐍 ▏ So SNAKE

   <!-- @sub -->
   <!-- @sub:example002.png.txt -->

      > holms run  -u - <<<'aаͣāãâȧäåₐᵃａ'
    
      00  U+  61 ▕ a ▏ Ll LATIN SMALL LETTER A
      01  U+ 430 ▕ а ▏ Ll CYRILLIC SMALL LETTER A
      03  U+ 363 ▕  ͣ ▏ Mn COMBINING LATIN SMALL LETTER A
      05  U+ 101 ▕ ā ▏ Ll LATIN SMALL LETTER A WITH MACRON
      07  U+  E3 ▕ ã ▏ Ll LATIN SMALL LETTER A WITH TILDE
      09  U+  E2 ▕ â ▏ Ll LATIN SMALL LETTER A WITH CIRCUMFLEX
      0b  U+ 227 ▕ ȧ ▏ Ll LATIN SMALL LETTER A WITH DOT ABOVE
      0d  U+  E4 ▕ ä ▏ Ll LATIN SMALL LETTER A WITH DIAERESIS
      0f  U+  E5 ▕ å ▏ Ll LATIN SMALL LETTER A WITH RING ABOVE
      11  U+2090 ▕ ₐ ▏ Lm LATIN SUBSCRIPT SMALL LETTER A
      14  U+1D43 ▕ ᵃ ▏ Lm MODIFIER LETTER SMALL A
      17  U+FF41 ▕ａ ▏ Ll FULLWIDTH LATIN SMALL LETTER A

   <!-- @sub -->
   <!-- @sub:example003.png.txt -->

      > holms run  -u - <<<'%‰∞8᪲?¿‽⚠⚠️'
    
      00  U+  25 ▕ % ▏ Po PERCENT SIGN
      01  U+2030 ▕ ‰ ▏ Po PER MILLE SIGN
      04  U+221E ▕ ∞ ▏ Sm INFINITY
      07  U+  38 ▕ 8 ▏ Nd DIGIT EIGHT
      08  U+1AB2 ▕  ᪲ ▏ Mn COMBINING INFINITY
      0b  U+  3F ▕ ? ▏ Po QUESTION MARK
      0c  U+  BF ▕ ¿ ▏ Po INVERTED QUESTION MARK
      0e  U+203D ▕ ‽ ▏ Po INTERROBANG
      11  U+26A0 ▕ ⚠ ▏ So WARNING SIGN
      14  U+26A0 ▕ ⚠ ▏ So WARNING SIGN
      17  U+FE0F ▕  ️ ▏ Mn VARIATION SELECTOR-16

   <!-- @sub -->
</details> 


Buffering
---------------------------------

The application works in two modes: **buffered** (the default if INPUT is a
file) and **unbuffered** (default when reading from stdin). Options `-b`/`-u`
explicitly override output mode regardless of the default setting.

In **buffered** mode the result begins to appear only after EOF is encountered
(i.e., the WHOLE file has been read to the buffer). This is suitable for short
and predictable inputs and produces the most compact output with fixed column
sizes.

The **unbuffered** mode comes in handy when input is an endless piped stream:
the results will be displayed in real time, as soon as the type of each byte
sequence is determined, but the output column widths are not fixed and can vary
as the process goes further.

> Despite the name, the app actually uses tiny (4 bytes) input buffer, but it's
> the only way to handle UTF-8 stream and distinguish valid sequences from broken
> ones; in truly unbuffered mode the output would consist of ASCII-7 characters
> (`0x00`-`0x7F`) and unrecognized binary data (`0x80`-`0xFF`) only, which is not
> something the application was made for.


Configuration / Advanced usage
----------------------------------
[//]: # (@sub:help.txt)

    Options:
      -b, --buffered / -u, --unbuffered
                            Explicitly set to wait for EOF before processing the
                            output (buffered), or to stream the results in
                            parallel with reading, as soon as possible
                            (unbuffered). See BUFFERING section above for the
                            details.
      -m, --merge           Replace all sequences of repeating characters with one
                            of each, together with initial length of the sequence.
      -g, --group           Group the input by code points (=count unique), sort
                            descending and display counts instead of normal
                            output. Implies '--merge' and forces buffered ('-b')
                            mode. Specifying the option twice ('-gg') results in
                            grouping by code point category instead, while doing
                            it thrice ('-ggg') makes the app group the input by
                            super categories.
      -o, --oneline         Remove all newline characters (0x0a LINE FEED) from
                            the output.
      -f, --format          Comma-separated list of columns to show (order is
                            preserved). Run 'holms format' to see the details.
      -n, --names           Display names instead of abbreviations. Affects `cat`
                            and `block` columns, but only if column in question is
                            already present on the screen. Note that these columns
                            can still display only the beginning of the attribute,
                            unless '-r' is provided.
      -a, --all             Display ALL columns.
      -r, --rigid           By default some columns can be compressed beyond the
                            nominal width, if all current values fit and there is
                            still space left. This option disables column
                            shrinking (but they still will be expanded when
                            needed).
      --decimal             Use decimal byte offsets instead of hexadecimal.
      -?, --help            Show this message and exit.

[//]: # (@sub)

Examples
--------------------------

### Output column selection

Option `-f`/`--filter` can be used to specify what columns to display. As an
alternative, there is an `-a`/`--all` option that enables displaying of all
currently available columns.

<details>
  <summary><b>Column availability depending on operating mode</b></summary>

  <div align="center">
    <img alt="example010" src="https://github.com/es7s/holms/assets/50381946/99248798-aecc-4a23-8703-fb412367beaa">
  </div>
</details>

Also `-m`/`--merge` option is demonstrated, which tells the app to collapse
repetitive characters into one line of the output while counting them:

<div align="center">
  <img alt="example005" src="https://github.com/es7s/holms/assets/50381946/fbb5817e-92ff-47be-a249-c70e0aa10c71">
</div>

<details>
   <summary>Plain text output</summary>
   <!-- @sub:example005.png.txt -->

      > holms run -m  phpstan.txt
    
      000  U+2B ▕ + ▏ Sm     PLUS SIGN
      001+ U+2D ▕ - ▏ Pd 27× HYPHEN-MINUS
      01c  U+2B ▕ + ▏ Sm     PLUS SIGN
      01d  U+20 ▕ ␣ ▏ Zs     SPACE
      01e  U+2B ▕ + ▏ Sm     PLUS SIGN
      01f+ U+2D ▕ - ▏ Pd 27× HYPHEN-MINUS
      03a  U+2B ▕ + ▏ Sm     PLUS SIGN
      03b  U+ A ▕ ↵ ▏ Cc     ASCII C0 [LF] LINE FEED
      03c  U+7C ▕ | ▏ Sm     VERTICAL LINE
      03d+ U+20 ▕ ␣ ▏ Zs 27× SPACE
     ...

   <!-- @sub -->
</details>

### Reading from pipeline

There is an official Unicode Consortium data file included in the repository for
test purposes, named [confusables.txt](tests/data/confusables.txt). In the next
example we extract line **#3620** using `sed`, delete all TAB (`0x08`) characters
and feed the result to the application. The result demonstrates various Unicode
dot/bullet code points:

<div align="center">
    <img alt="example006" src="https://github.com/es7s/holms/assets/50381946/2e4882fb-ce04-4548-87e6-01ede829e350">
</div>

<details>
   <summary>Plain text output</summary>
   <!-- @sub:example006.png.txt -->

      > sed confusables.txt -Ee 'sg' -e '3620!d' |
        holms run  -
    
      00  U+  B7 ▕ · ▏ Po MIDDLE DOT
      02  U+1427 ▕ ᐧ ▏ Lo CANADIAN SYLLABICS FINAL MIDDLE DOT
      05  U+ 387 ▕ · ▏ Po GREEK ANO TELEIA
      07  U+2022 ▕ • ▏ Po BULLET
      0a  U+2027 ▕ ‧ ▏ Po HYPHENATION POINT
      0d  U+2219 ▕ ∙ ▏ Sm BULLET OPERATOR
      10  U+22C5 ▕ ⋅ ▏ Sm DOT OPERATOR
      13  U+30FB ▕・ ▏ Po KATAKANA MIDDLE DOT
      16  U10101 ▕ 𐄁 ▏ Po AEGEAN WORD SEPARATOR DOT
      1a  U+FF65 ▕ ･ ▏ Po HALFWIDTH KATAKANA MIDDLE DOT
      1d  U+   A ▕ ↵ ▏ Cc ASCII C0 [LF] LINE FEED

   <!-- @sub -->
</details>

### Code points / categories statistics

`-g`/`--group` option can be used to count unique code points, and to compute
the occurrence rate of each one:

<div align="center">
  <img alt="example008" src="https://github.com/es7s/holms/assets/50381946/f6e79865-a365-4e75-93d6-8390d5d82495">
</div>

<details>
   <summary>Plain text output</summary>
   <!-- @sub:example008.png.txt -->

      > holms run -g  ./tests/data/confusables.txt
    
     U+  20 ▕ ␣ ▏ Zs   13% ███ 62732× SPACE
     U+   9 ▕ ⇥ ▏ Cc  7.3% █▊  36745× ASCII C0 [HT] HORIZONTAL TABULATION
     U+  41 ▕ A ▏ Lu  6.1% █▍  30555× LATIN CAPITAL LETTER A
     U+  49 ▕ I ▏ Lu  5.2% █▏  26063× LATIN CAPITAL LETTER I
     U+  45 ▕ E ▏ Lu  5.0% █▏  24992× LATIN CAPITAL LETTER E
     U+  54 ▕ T ▏ Lu  3.7% ▉   18776× LATIN CAPITAL LETTER T
     U+  4C ▕ L ▏ Lu  3.7% ▉   18763× LATIN CAPITAL LETTER L
     U+200E ▕ ▯ ▏ Cf  3.7% ▉   18494× LEFT-TO-RIGHT MARK
     U+   A ▕ ↵ ▏ Cc  2.9% ▋   14609× ASCII C0 [LF] LINE FEED
     U+  43 ▕ C ▏ Lu  2.9% ▋   14450× LATIN CAPITAL LETTER C
     ...

   <!-- @sub -->
</details>

When used twice (`-gg`) or thrice (`-ggg`), the application groups the input by
code point category or code point super category, respectively, which can be used
e.g. for frequency domain analysis:

<div align="center">
  <img alt="example011" src="https://github.com/es7s/holms/assets/50381946/fa816966-dbd7-4e2b-9be4-3b10b6883672">
  <img alt="example012" src="https://github.com/es7s/holms/assets/50381946/873c2406-c1cd-4587-91b3-003bc3684c7c">
</div>

<details>
   <summary>Plain text output</summary>
   <!-- @sub:example011.png.txt -->

      > holms run -gg  ./tests/data/confusables.txt
    
       53% ██████████ 266233× Uppercase_Letter
       13% ██▎         62748× Space_Separator
       10% █▉          51356× Control
      8.5% █▌          42511× Decimal_Number
      3.7% ▋           18497× Format
      3.0% ▌           14832× Other_Letter
      2.0% ▎            9778× Math_Symbol
      1.8% ▎            9261× Close_Punctuation
      1.8% ▎            9259× Open_Punctuation
      1.5% ▎            7525× Other_Punctuation
     ...

   <!-- @sub -->
   <!-- @sub:example012.png.txt -->

      > holms run -ggg  ./tests/data/confusables.txt
    
       57% ██████████ 284074× Letter
       14% ██▍         69853× Other
       13% ██▏         62750× Separator
      8.5% █▌          42796× Number
      5.9% █           29571× Punctuation
      2.2% ▍           11072× Symbol
      0.2% ▏             965× Mark

   <!-- @sub -->
</details>

### In-place type highlighting

When `--format` is specified exactly as a single `char` column: `--format=char`,
the application omits all the columns and prints the original file contents,
while highligting each character with a color that indicates its' Unicode
category. 

> Note that ASCII control codes, as well as Unicode ones, are kept
untouched and invisible.

<div align="center">
  <img alt="example007" src="https://github.com/es7s/holms/assets/50381946/788df0cd-9681-41dd-82fd-d6f477e8c4ac">
</div>

<details>
   <summary>Plain text output</summary>
   <!-- @sub:example007.png.txt -->

      > sed chars.txt -nEe 1,12p |
        holms run --format=char  -
    
       ! " # $ % & ' ( ) * + , - . /
     0 1 2 3 4 5 6 7 8 9 : ; < = > ?
     @ A B C D E F G H I J K L M N O
     P Q R S T U V W X Y Z [ \ ] ^ _
     ` a b c d e f g h i j k l m n o
     p q r s t u v w x y z { | } ~
       ¡ ¢ £ ¤ ¥ ¦ § ¨ © ª « ¬ ­ ® ¯
     ° ± ² ³ ´ µ ¶ · ¸ ¹ º » ¼ ½ ¾ ¿
     À Á Â Ã Ä Å Æ Ç È É Ê Ë Ì Í Î Ï
     Ð Ñ Ò Ó Ô Õ Ö × Ø Ù Ú Û Ü Ý Þ ß
     à á â ã ä å æ ç è é ê ë ì í î ï
     ð ñ ò ó ô õ ö ÷ ø ù ú û ü ý þ ÿ

   <!-- @sub -->
</details>


ASCII latin letters (`A-Za-z`) are colored in 50% gray color instead of regular
white on purpose — this can be extremely helpful when the task is to find
non-ASCII character(s) in an massive text of plain ASCII ones, or vice versa.

Below is a real example of broken characters which are the result of two
operations being applied in the wrong order: *UTF-8 decoding* and *URL %-based
unescaping*. This error is different from incorrect codepage selection errors,
which mess up the whole text or a part of it; all byte sequences are valid UTF-8
encoded code points, but the result differs from the origin and is completely 
unreadable nevertheless.

<div align="center">
  <img alt="example015" src="https://github.com/es7s/holms/assets/50381946/6cead36b-f026-49cc-8ba7-49bb25dd1456">
</div>


### ASCII C0 / C1 details

While developing the application I encountered strange (as it seemed to be at
the beginning) behaviour of Python interpreter, which encoded C1 control bytes
as two bytes of UTF-8, while C0 control bytes were displayed as sole bytes, like
it would have been encoded in a plain ASCII. Then there was a bit of researching
done.

According to [ISO/IEC 6429 (ECMA-48)](https://www.iso.org/standard/12782.html),
there are two types of ASCII control codes (to be precise, much more, but for
our purposes it's mostly irrelevant) — C0 and C1. The first one includes ASCII
code points `0x00`-`0x1F` and `0x7F` (some authors also include a regular space
character `0x20` in this list), and the characteristic property of this type is
that all C0 code points are encoded in UTF-8 **exactly the same** as they do in
7-bit US-ASCII ([ISO/IEC 646](https://www.iso.org/standard/4777.html)). This
helps to disambiguate exactly what type of encoding is used even for broken byte
sequences, considering the task is to tell if a byte represents sole code point
or is actually a part of multibyte UTF-8 sequence.

However, C1 control codes are represented by `0x80`-`0x9F` bytes, which also are
valid bytes for multibyte UTF-8 sequences. In order to distinguish the first
type from the second UTF-8 encodes them as two-byte sequences instead (`0x80` →
`0xC280`, etc.); also this applies not only to control codes, but to all other
[ISO/IEC 8859](https://www.iso.org/standard/28245.html) code points starting
from `0x80`.

With this in mind, let's see how the application reflects these differences.
First command produces several 8-bit ASCII C1 control codes, which are
classified as raw binary/non-UTF-8 data, while the second command's output
consists of the very same code points but being encoded in UTF-8 (thanks to
Python's full transparent Unicode support, we don't even need to bother much
about the encodings and such):

<div align="center">
  <img alt="example013" src="https://github.com/es7s/holms/assets/50381946/b2045a2d-a544-4989-b8bd-a32c9d2a6e7a">
</div>

<details>
   <summary>Plain text output</summary>
   <!-- @sub:example013.png.txt -->

      > printf "\x80\x90\x9f" && python3 -c 'print("\x80\x90\x9f", end="")' |
        holms run --names --decimal --all  -
    
     ⏨0  #0   0x    80  --  ▕ ▯ ▏ NON UTF-8 BYTE 0x80                                      -- Binary
     ⏨1  #1   0x    90  --  ▕ ▯ ▏ NON UTF-8 BYTE 0x90                                      -- Binary
     ⏨2  #2   0x    9f  --  ▕ ▯ ▏ NON UTF-8 BYTE 0x9F                                      -- Binary
    
     ⏨3  #3   0x c2 80 U+80 ▕ ▯ ▏ ASCII C1 [PC] PADDING CHARACTER            Latin-1 Supplem‥ Control
     ⏨5  #4   0x c2 90 U+90 ▕ ▯ ▏ ASCII C1 [DCS] DEVICE CONTROL STRING       Latin-1 Supplem‥ Control
     ⏨7  #5   0x c2 9f U+9F ▕ ▯ ▏ ASCII C1 [APC] APPLICATION PROGRAM COMMAND Latin-1 Supplem‥ Control

   <!-- @sub -->
</details>

Legend
------------------

The image below illustrates the color scheme developed for the app specifically,
to simplify distinguishing code points of one category from others.

<div align="center">
  <img alt="example009" src="https://github.com/es7s/holms/assets/50381946/6f66a7cd-a74c-4eef-9827-cad6535f0ff0">
</div>

Most frequently encountering control codes also have a unique character
replacements, which allows to recognize them without reading the label or
memorizing code point identifiers:

<div align="center">
  <img alt="example014" src="https://github.com/es7s/holms/assets/50381946/efad7252-9628-4ff8-9c37-177cd7ec26f1">
</div>

Changelog
------------------

[CHANGES.rst](CHANGES.rst)
