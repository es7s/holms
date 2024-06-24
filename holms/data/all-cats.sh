#!/bin/bash
#-------------------------------------------------------------------------------
# es7s/holms
# (c) 2024 A. Shavykin <0.delameter@gmail.com>
#-------------------------------------------------------------------------------
# shellcheck disable=SC2128,SC2059

FILE=./all-cats.bin
data=(
      1  # Cc ▕ ▯ ▏U+     1 ASCII C0 [SOH] START OF HEADING
   200D  # Cf ▕ ▯ ▏U+  200D ZERO WIDTH JOINER
   E0B0  # Co ▕  ▏U+  E0B0 PRIVATE USE
 10FFFE  # Cn ▕􏿾  ▏U+10FFFE (UNASSIGNED)
   D800  # Cs ▕ ▯ ▏U+  D800 UTF-16 SURROGATE
     61  # Ll ▕ a ▏U+    61 LATIN SMALL LETTER A
   1D43  # Lm ▕ ᵃ ▏U+  1D43 MODIFIER LETTER SMALL A
   600D  # Lo ▕怍 ▏U+  600D CJK UNIFIED IDEOGRAPH-600D
    1F2  # Lt ▕ ǲ ▏U+   1F2 LATIN CAPITAL LETTER D WITH SMALL LETTER Z
     41  # Lu ▕ A ▏U+    41 LATIN CAPITAL LETTER A
    93B  # Mc ▕ ऻ ▏U+   93B DEVANAGARI VOWEL SIGN OOE
    488  # Me ▕  ҈ ▏U+   488 COMBINING CYRILLIC HUNDRED THOUSANDS SIGN
    300  # Mn ▕  ̀ ▏U+   300 COMBINING GRAVE ACCENT
     30  # Nd ▕ 0 ▏U+    30 DIGIT ZERO
   2166  # Nl ▕ Ⅶ ▏U+  2166 ROMAN NUMERAL SEVEN
     B2  # No ▕ ² ▏U+    B2 SUPERSCRIPT TWO
     5F  # Pc ▕ _ ▏U+    5F LOW LINE
   2014  # Pd ▕ — ▏U+  2014 EM DASH
     29  # Pe ▕ ) ▏U+    29 RIGHT PARENTHESIS
     BB  # Pf ▕ » ▏U+    BB RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
     AB  # Pi ▕ « ▏U+    AB LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
     21  # Po ▕ ! ▏U+    21 EXCLAMATION MARK
     28  # Ps ▕ ( ▏U+    28 LEFT PARENTHESIS
     24  # Sc ▕ $ ▏U+    24 DOLLAR SIGN
     5E  # Sk ▕ ^ ▏U+    5E CIRCUMFLEX ACCENT
     2B  # Sm ▕ + ▏U+    2B PLUS SIGN
     A6  # So ▕ ¦ ▏U+    A6 BROKEN BAR
   2028  # Zl ▕ ▯ ▏U+  2028 LINE SEPARATOR
   2029  # Zp ▕ ▯ ▏U+  2029 PARAGRAPH SEPARATOR
   2006  # Zs ▕ ▯ ▏U+  2006 SIX-PER-E4M SPACE
)
extras=(
  $'\xff' # -- ▕ ▯ ▏      --  NON UTF-8 BYTE 0xFF
)

truncate --size 0 $FILE
{
  for i in ${data[*]}   ; do printf "\U$(printf %8s $i | tr ' ' 0)" ; done
  for b in ${extras[*]} ; do printf "$b"                            ; done
} >>$FILE
