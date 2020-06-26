#! /usr/bin/python3
import xml.etree.ElementTree as ET
import re

ns = {'html': "http://www.w3.org/1999/xhtml",
      'ab': "http://example.org/audiobook-schema"}

def html_ns(tag):
    return "{%s}%s" % (ns['html'], tag)
def ab_ns(tag):
    return "{%s}%s" % (ns['ab'], tag)

import sys
output_file = sys.argv[1]

def chapter_title_text(element):
    tag = element.tag
    if not isinstance(tag, str) and tag is not None:
        return

    t = element.text
    if t:
        yield t
        if tag == html_ns("div"):
            yield ": "
    for e in element:
        yield from chapter_title_text(e)
        t = e.tail
        if t:
            yield t

nav_map = ET.Element('navMap')
chapter = 0
for h2 in ET.parse('twir.xhtml').findall('./html:body/html:h2', ns):
    chapter += 1
    nav_point = ET.SubElement(nav_map, 'navPoint', {'playOrder': '%d' % chapter})
    nav_label = ET.SubElement(nav_point, 'navLabel')
    text = ET.SubElement(nav_label, 'text')
    title = ''.join(chapter_title_text(h2))
    text.text = re.sub('\s+', ' ', title.rstrip('*'))
    ET.SubElement(nav_point, 'content', {'src': 'twir_%d.xhtml' % chapter})

ET.register_namespace('', 'http://www.daisy.org/z3986/2005/ncx/')
output = ET.parse('toc-skeleton.xml')
output.getroot().append(nav_map)
output.write(output_file, encoding='UTF-8', xml_declaration=True)
