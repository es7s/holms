# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from collections import namedtuple

UnicodeCategory = namedtuple('UnicodeCategory', ['abbr', 'name', 'description'])


# : UnicodeCategory('LC', 'Cased_Letter',          'Lu | Ll | Lt'),
_CATEGORY_LIST = {
    UnicodeCategory('Lu',  'Uppercase_Letter',      'an uppercase letter'),
    UnicodeCategory('Ll',  'Lowercase_Letter',      'a lowercase letter'),
    UnicodeCategory('Lt',  'Titlecase_Letter',      'a digraph encoded as a single character, with first part uppercase'),
    UnicodeCategory('Lm',  'Modifier_Letter',       'a modifier letter'),
    UnicodeCategory('Lo',  'Other_Letter',          'other letters, including syllables and ideographs'),
    UnicodeCategory('L' ,  'Letter',                'Lu | Ll | Lt | Lm | Lo'),
    UnicodeCategory('Mn',  'Nonspacing_Mark',       'a nonspacing combining mark (zero advance width)'),
    UnicodeCategory('Mc',  'Spacing_Mark',          'a spacing combining mark (positive advance width)'),
    UnicodeCategory('Me',  'Enclosing_Mark',        'an enclosing combining mark'),
    UnicodeCategory('M' ,  'Mark',                  'Mn | Mc | Me'),
    UnicodeCategory('Nd',  'Decimal_Number',        'a decimal digit'),
    UnicodeCategory('Nl',  'Letter_Number',         'a letterlike numeric character'),
    UnicodeCategory('No',  'Other_Number',          'a numeric character of other type'),
    UnicodeCategory('N' ,  'Number',                'Nd | Nl | No'),
    UnicodeCategory('Pc',  'Connector_Punctuation', 'a connecting punctuation mark, like a tie'),
    UnicodeCategory('Pd',  'Dash_Punctuation',      'a dash or hyphen punctuation mark'),
    UnicodeCategory('Ps',  'Open_Punctuation',      'an opening punctuation mark (of a pair)'),
    UnicodeCategory('Pe',  'Close_Punctuation',     'a closing punctuation mark (of a pair)'),
    UnicodeCategory('Pi',  'Initial_Punctuation',   'an initial quotation mark'),
    UnicodeCategory('Pf',  'Final_Punctuation',     'a final quotation mark'),
    UnicodeCategory('Po',  'Other_Punctuation',     'a punctuation mark of other type'),
    UnicodeCategory('P' ,  'Punctuation',           'Pc | Pd | Ps | Pe | Pi | Pf | Po'),
    UnicodeCategory('Sm',  'Math_Symbol',           'a symbol of mathematical use'),
    UnicodeCategory('Sc',  'Currency_Symbol',       'a currency sign'),
    UnicodeCategory('Sk',  'Modifier_Symbol',       'a non-letterlike modifier symbol'),
    UnicodeCategory('So',  'Other_Symbol',          'a symbol of other type'),
    UnicodeCategory('S' ,  'Symbol',                'Sm | Sc | Sk | So'),
    UnicodeCategory('Zs',  'Space_Separator',       'a space character (of various non-zero widths)'),
    UnicodeCategory('Zl',  'Line_Separator',        'U+2028 LINE SEPARATOR only'),
    UnicodeCategory('Zp',  'Paragraph_Separator',   'U+2029 PARAGRAPH SEPARATOR only'),
    UnicodeCategory('Z' ,  'Separator',             'Zs | Zl | Zp'),
    UnicodeCategory('Cc',  'Control',               'a C0 or C1 control code'),
    UnicodeCategory('Cf',  'Format',                'a format control character'),
    UnicodeCategory('Cs',  'Surrogate',             'a surrogate code point'),
    UnicodeCategory('Co',  'Private_Use',           'a private-use character'),
    UnicodeCategory('Cn',  'Unassigned',            'a reserved unassigned code point or a noncharacter'),
    UnicodeCategory('C' ,  'Other',                 'Cc | Cf | Cs | Co | Cn'),
}

_CATEGORY_MAP = {v.abbr: v for v in _CATEGORY_LIST}


def resolve_category(abbr: str) -> UnicodeCategory:
    if cat := _CATEGORY_MAP.get(abbr):
        return cat
    raise LookupError(f"Invalid category: {abbr}")


def get_longest_name_length() -> int:
    return max(len(cat.name) for cat in _CATEGORY_LIST)
