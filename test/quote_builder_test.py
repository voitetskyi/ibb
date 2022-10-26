from unittest import TestCase

from ibb.util.quote_builder import str_to_quote


class QuoteBuilderTest(TestCase):

    def test_should_build_default_singe_bar(self):
        quotes = str_to_quote('|')
        self.assertEqual(0, quotes[0]['open'])
        self.assertEqual(100, quotes[0]['high'])
        self.assertEqual(0, quotes[0]['low'])
        self.assertEqual(0, quotes[0]['close'])

    def test_should_build_singe_bar(self):
        quotes = str_to_quote('|3412')
        self.assertEqual(30, quotes[0]['open'])
        self.assertEqual(40, quotes[0]['high'])
        self.assertEqual(10, quotes[0]['low'])
        self.assertEqual(20, quotes[0]['close'])

    def test_should_build_default_multiline_bar(self):
        quotes = str_to_quote('|\n|')
        self.assertEqual(0, quotes[0]['open'])
        self.assertEqual(200, quotes[0]['high'])
        self.assertEqual(0, quotes[0]['low'])
        self.assertEqual(0, quotes[0]['close'])

    def test_should_build_multiline_bar(self):
        quotes = str_to_quote('|0..5\n|')
        self.assertEqual(100, quotes[0]['open'])
        self.assertEqual(200, quotes[0]['high'])
        self.assertEqual(0, quotes[0]['low'])
        self.assertEqual(150, quotes[0]['close'])
