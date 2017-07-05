import unittest
import langtags

class LangTagsTests(unittest.TestCase):
    def testWellFormed(self):
        self.assertTrue(langtags.tag_is_well_formed("en"))
        self.assertTrue(langtags.tag_is_well_formed("en-Latn-US"))
        self.assertTrue(langtags.tag_is_well_formed("en-Latn-US-x-private-tag"))
        self.assertTrue(langtags.tag_is_well_formed("eng"))  # well-formed, but not valid
        self.assertTrue(langtags.tag_is_well_formed("cn"))  # well-formed, but not valid
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

    def testWellFormedAndValid(self):
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

        tag = langtags.Tag(langtags.normalize("pt-BR_abl1943"))
        self.assertEqual(str(tag), "pt-BR-abl1943")

        tag = langtags.Tag("pt-BR_abl1943", True)
        self.assertEqual(str(tag), "pt-BR-abl1943")
        self.assertEqual(str(tag.language), "pt")
        self.assertEqual(str(tag.region), "BR")

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


if __name__ == '__main__':
    unittest.main()
