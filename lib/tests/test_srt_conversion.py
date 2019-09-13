from __future__ import unicode_literals

import unittest

from pycaption import DFXPWriter, SRTReader, SRTWriter, WebVTTWriter

import six

from tests.mixins import DFXPTestingMixIn, SRTTestingMixIn, WebVTTTestingMixIn
from tests.samples.dfxp import SAMPLE_DFXP
from tests.samples.srt import SAMPLE_SRT
from tests.samples.webvtt import SAMPLE_WEBVTT_FROM_SRT


class SRTtoSRTTestCase(unittest.TestCase, SRTTestingMixIn):

    def test_srt_to_srt_conversion(self):
        caption_set = SRTReader().read(SAMPLE_SRT)
        results = SRTWriter().write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertSRTEquals(SAMPLE_SRT, results)


class SRTtoDFXPTestCase(unittest.TestCase, DFXPTestingMixIn):

    def test_srt_to_dfxp_conversion(self):
        caption_set = SRTReader().read(SAMPLE_SRT)
        results = DFXPWriter().write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertDFXPEquals(
            SAMPLE_DFXP, results,
            ignore_styling=True, ignore_spans=True
        )


class SRTtoWebVTTTestCase(unittest.TestCase, WebVTTTestingMixIn):

    def test_srt_to_webvtt_conversion(self):
        caption_set = SRTReader().read(SAMPLE_SRT)
        results = WebVTTWriter().write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_SRT, results)
