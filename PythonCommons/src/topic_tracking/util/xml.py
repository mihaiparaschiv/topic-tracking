from BeautifulSoup import UnicodeDammit
from lxml import etree


# XML / HTML parsing
# these functions can be used when the encoding is not specified in the Doctype

_xml_parser = etree.XMLParser()
_utf8_xml_parser = etree.XMLParser(encoding='utf-8')
_html_parser = etree.HTMLParser()
_utf8_html_parser = etree.HTMLParser(encoding='utf-8')

def parse_xml(text):
    parser = _xml_parser
    if isinstance(text, unicode):
        text = text.encode('utf-8')
        parser = _utf8_xml_parser
    return etree.fromstring(text, parser=parser)

def parse_html(text):
    parser = _html_parser
    if isinstance(text, unicode):
        text = text.encode('utf-8')
        parser = _utf8_html_parser
    return etree.fromstring(text, parser=parser)


# XML / HTML decoding
# these functions are used to transform web pages to unicode

def _decode(text, proposed_encoding, isHTML):
    converted = UnicodeDammit(text,
        isHTML=isHTML, overrideEncodings=(proposed_encoding,))
    if not converted.unicode:
        raise UnicodeDecodeError(
            "Failed to detect encoding, tried [%s]",
            ', '.join(converted.triedEncodings))
    return converted.unicode

def decode_xml(text, proposed_encoding):
    return _decode(text, proposed_encoding, False)

def decode_html(text, proposed_encoding):
    return _decode(text, proposed_encoding, True)