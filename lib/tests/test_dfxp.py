from __future__ import unicode_literals

import unittest

from pycaption import CaptionReadNoCaptions, DFXPReader
from pycaption.exceptions import (
    CaptionReadError, CaptionReadSyntaxError, InvalidInputError
)
from pycaption.geometry import (
    HorizontalAlignmentEnum, UnitEnum, VerticalAlignmentEnum
)

from tests.samples.dfxp import (
    DFXP_WITH_ALTERNATIVE_TIMING_FORMATS, SAMPLE_DFXP, SAMPLE_DFXP_EMPTY,
    SAMPLE_DFXP_EMPTY_PARAGRAPH,
    SAMPLE_DFXP_EMPTY_PARAGRAPH_WITH_MULTIPLE_NEWLINES,
    SAMPLE_DFXP_EMPTY_PARAGRAPH_WITH_NEWLINE, SAMPLE_DFXP_SYNTAX_ERROR,
)


class DFXPReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(DFXPReader().detect(SAMPLE_DFXP))

    def test_caption_length(self):
        captions = DFXPReader().read(SAMPLE_DFXP)
        self.assertEqual(7, len(captions.get_captions(u"en-US")))

    def test_proper_timestamps(self):
        captions = DFXPReader().read(SAMPLE_DFXP)
        paragraph = captions.get_captions(u"en-US")[2]

        self.assertEqual(17000000, paragraph.start)
        self.assertEqual(18752000, paragraph.end)

    def test_offset_time(self):
        reader = DFXPReader()
        self.assertEqual(1, reader._translate_time(u"0.001ms"))
        self.assertEqual(2000, reader._translate_time(u"2ms"))
        self.assertEqual(1000000, reader._translate_time(u"1s"))
        self.assertEqual(1234567, reader._translate_time(u"1.234567s"))
        self.assertEqual(180000000, reader._translate_time(u"3m"))
        self.assertEqual(14400000000, reader._translate_time(u"4h"))
        # Tick values are not supported
        self.assertRaises(
            InvalidInputError, reader._translate_time, u"2.3t"
        )

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            DFXPReader().read, SAMPLE_DFXP_EMPTY)

    def test_invalid_markup_is_properly_handled(self):
        captions = DFXPReader().read(SAMPLE_DFXP_SYNTAX_ERROR)
        self.assertEqual(2, len(captions.get_captions(u"en-US")))

    def test_caption_error_for_invalid_positioning_values(self):
        invalid_value_dfxp = (
            SAMPLE_DFXP_INVALID_POSITIONING_VALUE_TEMPLATE
            .format(origin=u"px 5px")
        )
        self.assertRaises(
            CaptionReadSyntaxError, DFXPReader().read,
            invalid_value_dfxp
        )

    def test_caption_error_for_invalid_or_unsupported_positioning_units(self):
        invalid_dfxp = (
            SAMPLE_DFXP_INVALID_POSITIONING_VALUE_TEMPLATE
            .format(origin=u"6foo 7bar")
        )
        self.assertRaises(
            CaptionReadSyntaxError, DFXPReader().read,
            invalid_dfxp
        )

    def test_individual_timings_of_captions_with_matching_timespec_are_kept(self):  # noqa: E501
        captionset = DFXPReader().read(
            SAMPLE_DFXP_MULTIPLE_CAPTIONS_WITH_THE_SAME_TIMING
        )
        expected_timings = [(9209000, 12312000)] * 3
        actual_timings = [(c_.start, c_.end) for c_ in
                          captionset.get_captions('en-US')]
        self.assertEqual(expected_timings, actual_timings)

    def test_individual_texts_of_captions_with_matching_timespec_are_kept(self):  # noqa: E501
        captionset = DFXPReader().read(
            SAMPLE_DFXP_MULTIPLE_CAPTIONS_WITH_THE_SAME_TIMING
        )

        expected_texts = ['Some text here',
                          'Some text there',
                          'Caption texts are everywhere!']
        actual_texts = [c_.nodes[0].content for c_ in
                        captionset.get_captions("en-US")]

        self.assertEqual(expected_texts, actual_texts)

    def test_individual_layouts_of_captions_with_matching_timespec_are_kept(self):  # noqa: E501
        captionset = DFXPReader().read(
            SAMPLE_DFXP_MULTIPLE_CAPTIONS_WITH_THE_SAME_TIMING
        )
        expected_layouts = [
            (((10, UnitEnum.PERCENT), (10, UnitEnum.PERCENT)), None, None,
             (HorizontalAlignmentEnum.CENTER,
              VerticalAlignmentEnum.BOTTOM)),
            (((40, UnitEnum.PERCENT), (40, UnitEnum.PERCENT)), None, None,
             (HorizontalAlignmentEnum.CENTER,
              VerticalAlignmentEnum.BOTTOM)),
            (((10, UnitEnum.PERCENT), (70, UnitEnum.PERCENT)), None, None,
             (HorizontalAlignmentEnum.CENTER,
              VerticalAlignmentEnum.BOTTOM))]
        actual_layouts = [c_.layout_info.serialized() for c_ in
                          captionset.get_captions('en-US')]

        self.assertEqual(expected_layouts, actual_layouts)

    def test_properly_converts_timing(self):
        caption_set = DFXPReader().read(
            DFXP_WITH_ALTERNATIVE_TIMING_FORMATS)
        caps = caption_set.get_captions('en-US')
        self.assertEqual(caps[0].start, 1900000)
        self.assertEqual(caps[0].end, 3050000)
        self.assertEqual(caps[1].start, 4000000)
        self.assertEqual(caps[1].end, 5200000)

    def test_empty_paragraph(self):
        try:
            DFXPReader().read(SAMPLE_DFXP_EMPTY_PARAGRAPH)
        except CaptionReadError:
            self.fail("Failing on empty paragraph")

    def test_empty_paragraph_with_newline(self):
        try:
            DFXPReader().read(SAMPLE_DFXP_EMPTY_PARAGRAPH_WITH_NEWLINE)
        except CaptionReadError:
            self.fail("Failing on empty paragraph with one newline")

    def test_empty_paragraph_with_multiple_newlines(self):
        try:
            DFXPReader().read(
                SAMPLE_DFXP_EMPTY_PARAGRAPH_WITH_MULTIPLE_NEWLINES)
        except CaptionReadError:
            self.fail("Failing on empty paragraph with multiple newlines")


SAMPLE_DFXP_INVALID_POSITIONING_VALUE_TEMPLATE = u"""\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <layout>
   <region tts:origin="{origin}" xml:id="bottom"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" region="bottom">
    ( clock ticking )
   </p>
  </div>
 </body>
</tt>"""  # noqa: E501

# TODO - notice that there's no "bottom" region specified in the <layout>
# region, but it's referenced by the <div>. Decide if this is ok enough
SAMPLE_DFXP_MULTIPLE_CAPTIONS_WITH_THE_SAME_TIMING = u"""\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <layout>
   <region tts:origin="10% 10%" xml:id="b1"/>
   <region tts:origin="40% 40%" xml:id="b2"/>
   <region tts:origin="10% 70%" xml:id="b3"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" region="b1">
    Some text here
   </p>
   <p begin="00:00:09.209" end="00:00:12.312" region="b2">
    Some text there
   </p>
   <p begin="00:00:09.209" end="00:00:12.312" region="b3">
    Caption texts are everywhere!
   </p>
  </div>
 </body>
</tt>"""  # noqa: E501
