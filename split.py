#! /usr/bin/python3
import xml.etree.ElementTree as ET
import re

ns = {'html': "http://www.w3.org/1999/xhtml",
      'ab': "http://example.org/audiobook-schema"}

def html_ns(tag):
    return "{%s}%s" % (ns['html'], tag)
def ab_ns(tag):
    return "{%s}%s" % (ns['ab'], tag)

ET.register_namespace('', ns['html'])
ET.register_namespace('ab', ns['ab'])
tree = ET.parse('twir.xhtml')
n_chapters = len(tree.findall('./html:body/html:h2', ns))
assert n_chapters == 40
for i in range(1, n_chapters + 1):
    tree = ET.parse('twir.xhtml')
    chapter = 0
    body = tree.find('./html:body', ns)
    for e in list(body):
        if e.tag == html_ns('h2'):
            chapter += 1
        if chapter != i:
            body.remove(e)
    tree.write('twir_%d.xhtml' % i,
               encoding='UTF-8',
               xml_declaration=True)
