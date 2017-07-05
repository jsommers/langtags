"""
langtags.py.

FIXME

Utility module with one function to check whether a language tag is
well-formed according to BCP47 (https://tools.ietf.org/html/bcp47)
but not if it is valid.
"""
import sys
import re
import os
import enum
from copy import copy
from collections import OrderedDict, defaultdict


# based on http://schneegans.de/lv/
_bcp47_regex = re.compile("""
^
(
  (
    (
      (
        (?P<language23>
          [a-z]{2,3}
        )
        (-
          (?P<extlang>
            [a-z]{3}
          )
        ){0,3}
      )
      |
      (?P<language4>
        [a-z]{4}
      )
      |
      (?P<language58>
        [a-z]{5,8}
      )
    )

    (-(?P<script>
      [a-z]{4}
    ))?

    (-(?P<region>
      [a-z]{2}
      |
      [0-9]{3}
    ))?

    (-
      (?P<variant>
        [a-z0-9]{5,8}
        |
        [0-9][a-z0-9]{3}
      )
    )*

    (-
      (?P<extensions>
        [a-wy-z0-9]
        (-
          [a-z0-9]{2,8}
        )+
      )
    )*

    (-
      (?P<privateusesubtags>x
        (-
          (
            [a-z0-9]{1,8}
          )
        )+
      )
    )?
  )
  |
  (?P<privateusetags>
    x(-
      (
        [a-z0-9]{1,8}
      )
    )+
  )
  |
  (?P<grandfathered>
    (?P<irregular>
      en-GB-oed |
      i-ami |
      i-bnn |
      i-default |
      i-enochian |
      i-hak |
      i-klingon |
      i-lux |
      i-mingo |
      i-navajo |
      i-pwn |
      i-tao |
      i-tay |
      i-tsu |
      sgn-BE-FR |
      sgn-BE-NL |
      sgn-CH-DE
    )
    |
    (?P<regular>
      art-lojban |
      cel-gaulish |
      no-bok |
      no-nyn |
      zh-guoyu |
      zh-hakka |
      zh-min |
      zh-min-nan |
      zh-xiang
    )
  )
)
$
""", re.VERBOSE|re.IGNORECASE)


def tag_is_well_formed(s):
    """Check whether a language tag is well-formed according to bcp47"""
    return _bcp47_regex.match(s) is not None


def extract_language_subtag(s):
    """
    Return the language subtag (not any other subtags) as a string.

    Do some normalization in order to try to get to a valid subtag:
    Replace _ with - and / with -.
    RFC5646 requires -, but many sites don't comply...  thanks.
    Lower-case it for compatibility with language-subtag-registry.
    """
    return normalize_language_tag(s).split('-')[0].lower()


def normalize(s):
    """Attempt to modify language tag content to get it into the expected form."""
    return s.replace('_', '-').replace('/', '-')


class InvalidSubtagError(Exception):
    pass


class MalformedTagError(Exception):
    pass


class SubtagRecordType(enum.IntEnum):
    Language = 1
    Extlang = 2
    Script = 3
    Region = 4
    Variant = 5
    Grandfathered = 6
    Redundant = 7
    Private = 8
    Extensions = 9


_regex_name_to_enum = OrderedDict([
    ('language23', SubtagRecordType.Language),
    ('language4', SubtagRecordType.Language),
    ('language58', SubtagRecordType.Language),
    ('extlang', SubtagRecordType.Extlang),
    ('script', SubtagRecordType.Script),
    ('region', SubtagRecordType.Region),
    ('variant', SubtagRecordType.Variant),
    ('grandfathered', SubtagRecordType.Grandfathered),
    ('extensions', SubtagRecordType.Extensions),
    ('privateusesubtags', SubtagRecordType.Private),
    ('privateusetags', SubtagRecordType.Private),
])


class LanguageSubtagRegistry(object):
    def __init__(self):
        self._recs = {}
        for e in SubtagRecordType:
            if e == SubtagRecordType.Private:
                self._recs[e] = defaultdict(str)
            else:
                self._recs[e] = {}

    def match(self, tag):
        """Lookup subtag objects for each subtag in a full tag, e.g., zh-Hant-CN"""
        mobj = re.match(_bcp47_regex, tag)
        if mobj is None:
            return None

        objs = []
        gdict = mobj.groupdict()
        for k, v in _regex_name_to_enum.items():
            if gdict[k] is not None:
                if v == SubtagRecordType.Private:
                    r = SubtagRegistryRecord({'Type': 'private', 
                                              'Tag': gdict[k]})
                else:
                    r = self._recs[v].get(gdict[k].lower())
                    if r is None:
                        raise InvalidSubtagError(gdict[k])
                objs.append(r)
        return objs

    def __str__(self):
        result = []
        for rectype in SubtagRecordType:
            result.append("{}: {}".format(rectype.name, len(self._recs[rectype])))
        return ', '.join(result)

    @staticmethod
    def load(infile="language-subtag-registry"):
        def _extract_info(xlines):
            xdict = {}
            for line in xlines:
                if ': ' not in line:
                    break
                try:
                    idx = line.find(':')
                    if idx == -1:
                        raise ValueError("Failed on line {}".format(line))
                    key = line[:idx].strip()
                    val = line[(idx+1):].strip()
                except ValueError:
                    print("Failed on line {line}".format(line=line))
                    sys.exit(0)
                xdict[key] = val
            return xdict

        def _load_group(inp):
            line = inp.readline()
            xlines = []
            while line and not line.startswith('%%'):
                # handle line continuation
                if line.startswith('  '):
                    xlines[-1] += ' ' + line.strip()
                else:
                    xlines.append(line.strip())
                line = inp.readline()
            return _extract_info(xlines)

        reg = LanguageSubtagRegistry()
        recs = reg._recs

        location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        with open(os.path.join(location, infile)) as inp:
            line = inp.readline()
            # first, eat first 2 lines to get to first record
            while not line.startswith('%%'):
                line = inp.readline()

            while True:
                xgroup = _load_group(inp)
                if not xgroup:
                    break
                recobj = SubtagRegistryRecord(xgroup)
                # NB: put dict keys in lowercase
                recs[recobj.rectype][recobj.subtag.lower()] = recobj
        return reg


class SubtagRegistryRecord(object):
    def __init__(self, rec):
        self._type = getattr(
            SubtagRecordType.Language, rec.get('Type').capitalize())
        if 'Subtag' in rec:
            self._subtag = rec.get('Subtag')
            self._tag = self._subtag
        else:
            self._tag = rec.get('Tag')
            self._subtag = self._tag
        self._description = rec.get('Description', '')
        self._added = rec.get('Added', '')
        self._comments = rec.get('Comments', '')
        if 'Deprecated' in rec:
            self._deprecated = True
            self._deprecated_date = rec['Deprecated']
        else:
            self._deprecated = False
        self._preferred_value = rec.get('Preferred-Value', '')
        self._supress_script = rec.get('Supress-Script', '')
        self._macrolanguage = rec.get('Macrolanguage', '')
        self._scope = rec.get('Scope', '')
        self._prefix = rec.get('Prefix', '')

    @property
    def rectype(self):
        return self._type

    @property
    def scope(self):
        return self._scope

    @property
    def subtag(self):
        return self._subtag

    @property
    def tag(self):
        return self._tag

    @property
    def macrolanguage(self):
        return self._macrolanguage

    @property
    def added(self):
        return self._added

    @property
    def comments(self):
        return self._comments

    @property
    def description(self):
        return self._description

    @property
    def preferred_value(self):
        return self._preferred_value

    @property
    def prefix(self):
        return self._prefix

    @property
    def supress_script(self):
        return self._supress_script

    def __str__(self):
        if self._type == SubtagRecordType.Region:
            return self._subtag.upper()
        elif self._type == SubtagRecordType.Script:
            return self._subtag.capitalize()
        return self._subtag.lower()


class Tag(object):
    def __init__(self, strtag='', should_normalize=False):
        if strtag:
            if should_normalize:
                strtag = normalize(strtag)
            subs = _registry.match(strtag)
            if subs is None:
                raise MalformedTagError(strtag)
            else:
                self._subtags = subs
        else:
            self._subtags = []

        self._byrectype = {}
        for s in self._subtags:
            self._byrectype[s.rectype.name.lower()] = s

    def __getattr__(self, attr):
        if attr in self._byrectype:
            return self._byrectype[attr]

    def __getitem__(self, idx):
        if idx < 0:
            idx = len(self._subtags) + idx
        return self._subtags[idx]

    def __str__(self):
        return "-".join([str(s) for s in self._subtags])

    def __len__(self):
        return len(self._subtags)


# global object; the subtag registry
_registry = LanguageSubtagRegistry.load()
