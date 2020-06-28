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
output_type = sys.argv[2]

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

def commit(content, unit):
    title = ''.join(chapter_title_text(unit[0]))
    title = title.rstrip('*')
    title = re.sub('\s+', ' ', title)
    content += [{'title': title, 'content': unit}]

def get_content(et):
    content = []

    n_h2 = 0
    body = et.find('./html:body', ns)
    unit = []
    for e in body:
        if e.tag == html_ns('h2'):
            if n_h2 > 0:
                commit(content, unit)
                unit = []
            n_h2 += 1
        unit += [e]
    commit(content, unit)
    return content
    
content = get_content(ET.parse('twir.xhtml'))

if output_type == 'epub':
    nav_map = ET.Element('navMap')
    for chapter, number in zip(content, range(len(content))):
        nav_point = ET.SubElement(nav_map, 'navPoint',
                                  {'playOrder': '%d' % (number + 1)})
        nav_label = ET.SubElement(nav_point, 'navLabel')
        text = ET.SubElement(nav_label, 'text')
        text.text = chapter['title']
        ET.SubElement(nav_point, 'content',
                      {'src': 'twir_%d.xhtml' % number})

    ET.register_namespace('', 'http://www.daisy.org/z3986/2005/ncx/')
    output = ET.parse('toc-skeleton.xml')
    output.getroot().append(nav_map)
    output.write(output_file, encoding='UTF-8', xml_declaration=True)
elif output_type == 'web':
    ET.register_namespace('', ns['html'])
    ET.register_namespace('ab', ns['ab'])
    output = ET.parse('index-skeleton.xhtml')
    nav = output.find('.//html:ul[@id="toc"]', ns)
    for chapter, number in zip(content, range(len(content))):
        item = ET.SubElement(nav, 'li')
        a = ET.SubElement(item, 'a', {'href': 'twir_%d.xhtml' % number})
        a.text = chapter['title']
    output.write(output_file, encoding='UTF-8', xml_declaration=True)
    
