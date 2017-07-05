"""
validlang.py.

Utility module with one function to check whether a language tag is
well-formed according to BCP47 (https://tools.ietf.org/html/bcp47)
but not if it is valid.
"""
import sys
import re
import enum
import string
from collections import Counter, defaultdict
import codecs


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
      x(?P<privateusesubtags>-
        (
          [a-z0-9]{1,8}
        )
      )+
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


def well_formed_bcp47(s):
    """Check whether a language tag is well-formed according to bcp47"""
    mobj = _bcp47_regex.match(s)
    if mobj is not None:
        return mobj.groupdict()
    return None


def extract_language_subtag(s):
    """
    Return the language subtag (not any other subtags) as a string.

    Do some normalization in order to try to get to a valid subtag:
    Replace _ with - and / with -.
    RFC5646 requires -, but many sites don't comply...  thanks.
    Lower-case it for compatibility with language-subtag-registry.
    """
    return normalize_language_tag(s).split('-')[0].lower()


def normalize_language_tag(s):
    """Attempt to modify language tag content to get it into the expected form."""
    return s.replace('_', '-').replace('/', '-')


def is_language_tag_well_formed(s):
    return well_formed_bcp47(s) is not None


class SubtagRecordType(enum.IntEnum):
    Language = 1
    Extlang = 2
    Script = 3
    Region = 4
    Variant = 5
    Grandfathered = 6
    Redundant = 7
    Private = 8


class LanguageSubtagRegistry(object):
    def __init__(self):
        self._recs = {}

    def lookup(self, subtag):
        """Get the record corresponding to a particular subtag (e.g., en, es, CN, Latn)"""
        subtag = subtag.lower()
        for rectype in SubtagRecordType:
            obj = self._recs[rectype].get(subtag, None)
            if obj is not None:
                return obj
        return None

    def lookup_language(self, subtag):
        """
        Get the record corresponding to a particular language subtag.

        Only check Language record types.
        Return the record or None if the subtag doesn't exist.
        """
        return self._recs[SubtagRecordType.Language].get(subtag, None)

    def lookup_region(self, subtag):
        """Get the record corresponding to a particular region subtag."""
        return self._recs[SubtagRecordType.Region].get(subtag, None)

    def lookup_full_tag(self, tag):
        """Lookup subtag objects for each subtag in a full tag, e.g., zh-Hant-CN"""
        objs = []
        private = False
        for subtag in normalize_language_tag(tag).split('-'):
            if subtag == 'x':
                private = True
                continue

            if private:
                objs.append(SubtagRegistryRecord({'Type': 'private', 'Subtag': subtag}))
            else:
                objs.append(self.lookup(subtag))
        return objs

    def __contains__(self, subtag):
        """Check whether the registry contains the given subtag (could be any type of subtag)"""
        return self.lookup(subtag) is not None

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

        recs = defaultdict(dict)
        reg = LanguageSubtagRegistry()
        reg._recs = recs

        with open(infile) as inp:
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
    def macrolanguage(self):
        return self._macrolanguage

    def is_language(self):
        self._type == SubtagRecordType.Language

    def __str__(self):
        return "{} {} ({})".format(self._subtag, self._description, self._type.name)


def get_langreg():
    return LanguageSubtagRegistry.load()


if __name__ == '__main__':
    # import sys
    # print("> ", end='', flush=True)
    # line = sys.stdin.readline()
    # while line:
    #     tag = line.strip()
    #     result = well_formed_bcp47(tag)
    #     print(result)
    #     print("> ", end='', flush=True)
    #     line = sys.stdin.readline()

    reg = LanguageSubtagRegistry.load()
    print(reg)
    print('en' in reg)
    print('eng' in reg)
    print('cn' in reg)
    print('zh' in reg)
    rec = reg.lookup('far')
    print(rec)
    rec = reg.lookup('fa')
    print(rec)

    olist = reg.lookup_full_tag('zh-Hant-CN')
    print([str(o) for o in olist])

    olist = reg.lookup_full_tag('zh-Hant-CN-x-private1-private2')
    print([str(o) for o in olist])

    print(is_language_tag_well_formed('zh-Hant-CN-x-private1-private2'))
