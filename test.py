import unittest
import langtags
import datetime


class LangTagsTests(unittest.TestCase):
    def testWellFormed(self):
        self.assertTrue(langtags.tag_is_well_formed("en"))
        self.assertTrue(langtags.tag_is_well_formed("en-Latn-US"))
        self.assertTrue(langtags.tag_is_well_formed(
            "en-Latn-US-x-private-tag"))
        self.assertTrue(langtags.tag_is_well_formed("eng"))
        self.assertTrue(langtags.tag_is_well_formed("cn"))
        self.assertTrue(langtags.tag_is_well_formed("zh-Hant-CN"))
        self.assertTrue(langtags.tag_is_well_formed("far"))
        self.assertTrue(langtags.tag_is_well_formed("zh-yue"))
        self.assertTrue(langtags.tag_is_well_formed("mn-Cyrl"))
        self.assertTrue(langtags.tag_is_well_formed("de-DE-1996"))
        self.assertTrue(langtags.tag_is_well_formed("pt-BR-abl1943"))
        self.assertTrue(langtags.tag_is_well_formed("en-GB-oed"))
        self.assertTrue(langtags.tag_is_well_formed("i-klingon"))
        self.assertTrue(langtags.tag_is_well_formed("x-not-a-language"))

        self.assertFalse(langtags.tag_is_well_formed("en-US-Latn"))
        self.assertFalse(langtags.tag_is_well_formed("i-english"))


    def testTagConstruction(self):
        tag = langtags.Tag("i-klingon")
        self.assertEqual(str(tag), "i-klingon")
        self.assertEqual(tag.grandfathered.subtag, "i-klingon")
        self.assertEqual(len(tag), 1)
        self.assertEqual(tag[0].preferred_value, "tlh")
        self.assertEqual(tag.grandfathered.preferred_value, "tlh")

        tag = langtags.Tag("en-Latn-US")
        self.assertEqual(str(tag), "en-Latn-US")
        self.assertEqual(tag.language.subtag, "en")
        self.assertEqual(tag.language.subtag, "en")
        self.assertEqual(tag.script.subtag, "Latn")
        self.assertEqual(tag.region.subtag, "US")
        self.assertEqual(len(tag), 3)
        self.assertEqual(tag[-1].subtag, "US")
        self.assertEqual(tag[-2].subtag, "Latn")
        self.assertEqual(tag[-3].subtag, "en")

        tag = langtags.Tag("en-latn-us")
        self.assertEqual(str(tag), "en-Latn-US")
        self.assertEqual(tag.script.subtag, "Latn")
        self.assertEqual(tag.region.subtag, "US")

        tag = langtags.Tag("de-DE-1996")
        self.assertEqual(str(tag), "de-DE-1996")
        self.assertEqual(tag.variant.subtag, "1996")

        tag = langtags.Tag("de-de-1996")
        self.assertEqual(str(tag), "de-DE-1996")

        with self.assertRaises(langtags.MalformedTagError):
            langtags.Tag("pt-BR_abl1943")

        tag = langtags.Tag("pt-BR_abl1943", normalize=True)
        self.assertEqual(str(tag), "pt-BR-abl1943")

        tag = langtags.Tag("pt-BR_abl1943", normalize=True)
        self.assertEqual(str(tag), "pt-BR-abl1943")
        self.assertEqual(str(tag.language), "pt")
        self.assertEqual(str(tag.region), "BR")

        tag = langtags.Tag('id')
        self.assertEqual(tag.language.tag, 'id')
        self.assertEqual(tag.language.subtag, 'id')
        self.assertEqual(tag.language.subtag, 'id')
        self.assertEqual(tag.language.suppress_script, 'Latn')
        self.assertEqual(tag.language.macrolanguage, 'ms')
        self.assertEqual(tag.language.scope, '')
        self.assertFalse(tag.language.is_deprecated)
        self.assertIsNone(tag.language.deprecated_date)
        self.assertEqual(tag[0], tag.language)

        tag = langtags.Tag('afa')
        self.assertEqual(tag.language.scope, 'collection')
        self.assertIsNotNone(tag.language.description)
        self.assertEqual(tag.language.added, datetime.date(2005, 10, 16))
        self.assertFalse(tag.language.is_deprecated)

        tag = langtags.Tag('bn')
        # two description lines in this record; make sure there are 2 lines
        self.assertEqual(tag.language.description.count('\n'), 1)

        tag = langtags.Tag('ar-abv')
        self.assertEqual(tag.language.subtag, 'ar')
        self.assertEqual(tag.extlang.subtag, 'abv')
        self.assertEqual(tag.extlang.prefix, 'ar')
        self.assertEqual(tag.extlang.macrolanguage, 'ar')
        self.assertEqual(tag.extlang.preferred_value, 'abv')
        self.assertEqual(
            tag.extlang.rectype, langtags.SubtagRecordType.Extlang)
        self.assertEqual(
            tag.language.rectype, langtags.SubtagRecordType.Language)

        tag = langtags.Tag('abv')
        self.assertEqual(
            tag.language.rectype, langtags.SubtagRecordType.Language)

        tag = langtags.Tag('jw')
        self.assertIn('error', tag.language.comments)

        with self.assertRaises(langtags.MalformedTagError):
            langtags.Tag("en-US-Latn")

        with self.assertRaises(langtags.InvalidSubtagError):
            langtags.Tag("cn-CN")

        with self.assertRaises(langtags.InvalidSubtagError):
            langtags.Tag("eng")

        tag = langtags.Tag("x-private-stuff")
        self.assertEqual(str(tag), "x-private-stuff")
        self.assertEqual(tag.private.subtag, "x-private-stuff")

        tag = langtags.Tag("zh-hant-cn-x-other-private-stuff")
        self.assertEqual(str(tag), "zh-Hant-CN-x-other-private-stuff")

        with self.assertRaises(langtags.MalformedTagError):
            langtags.Tag()


    def testRepr(self):
        tag = langtags.Tag("cy-latn-gb")
        self.assertEqual(str(tag), "cy-Latn-GB")
        trep = repr(tag)
        from langtags import Subtag, Tag
        xtag = eval(trep)
        self.assertEqual(str(xtag), 'cy-Latn-GB')
        xreg = eval(repr(xtag.region))
        self.assertEqual(xreg.subtag, 'GB')
        xlang = eval(repr(xtag.language))
        self.assertEqual(xlang.subtag, 'cy')
        self.assertEqual(str(xtag.script), 'Latn')
        self.assertIsNone(xtag.extlang)
        self.assertIsNone(xtag.variant)
        self.assertIsNone(xtag.grandfathered)
        self.assertIsNone(xtag.redundant)
        self.assertIsNone(xtag.private)
        self.assertIsNone(xtag.extensions)
        tag = langtags.Tag('i-klingon')
        xtag = eval(repr(tag))
        self.assertEqual(xtag.grandfathered.tag, 'i-klingon')


    def testTagIsValid(self):
        self.assertTrue(langtags.tag_is_valid("en"))
        self.assertFalse(langtags.tag_is_valid("en-XX"))
        self.assertFalse(langtags.tag_is_valid("13346"))


    def testIterTags(self):
        with self.assertRaises(ValueError):
            langtags.LanguageSubtagRegistry.itertags(-1)
            
        titer = langtags.LanguageSubtagRegistry.itertags(langtags.SubtagRecordType.Language)
        self.assertIsNotNone(titer is not None)
        self.assertTrue(len(list(titer)) > 100) # safely > 100 lang tags


if __name__ == '__main__':
    unittest.main()
