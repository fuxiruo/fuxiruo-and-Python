import logging
import unittest
from tinyxmlparse import TinyXmlParse,TinyXmlException

LOG_FORMAT = '[%(asctime)s][%(levelname)5s][%(module)s:%(funcName)s][%(threadName)10s]->%(message)s'

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(LOG_FORMAT)

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

testStr = """
<?xml version="1.0"?>
<stop version="1.1">
	<id>14791 这里有中文</id>
	<nm>Clark &amp; Balmoral</nm>
	<sri>
		<rt>22</rt>
		<d>North Bound</d>
		<dd>North Bound</dd>
	</sri>
	<cr ui="4" ty="5">22</cr>
    <selfclosetag1 tt="666"/>
    <selfclosetag2 tt=":/abc"/>
	<pre>
		<pt>5 MIN</pt>
		<fd>Howard</fd>
		<v>1378</v>
		<rn>22</rn>
	</pre>
	<pre tt="uiui">
		<pt>15 MIN</pt>
		<fd>Howard</fd>
		<v>1867</v>
		<rn>22</rn>
	</pre>
</stop>
"""

fail_test_str_with_no_close = """
<sri>
    <rt>22</rt>
    <d>North Bound</d>
    <dd>North Bound<dd>
</sri>
"""

fail_test_str_with_no_right = """
<sri
    <rt>22</rt>
    <d>North Bound</d>
    <dd>North Bound<dd>
</sri>
"""

class XmlTestCase(unittest.TestCase):
    def try_parse(self, dataStr):
        tiny_xml = TinyXmlParse()
        for line in dataStr.splitlines():
            tiny_xml.feed_line(line)
            tiny_xml.parse()
        tiny_xml.check_single_tags()
        return True

    def setUp(self):
        pass

    def test_pass(self):
        self.assertEqual(self.try_parse(testStr
        ), True)

    def test_fail(self):
        with self.assertRaises(TinyXmlException):
            self.try_parse('test')

    def test_fail_no_close(self):
        with self.assertRaisesRegex(TinyXmlException, 'tag not close'):
            self.try_parse(fail_test_str_with_no_close)

    def test_fail_no_right(self):
        with self.assertRaisesRegex(TinyXmlException, '< expect V|> but < found'):
            self.try_parse(fail_test_str_with_no_right)

unittest.main(verbosity=2)
