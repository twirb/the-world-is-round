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
target_chapter = int(sys.argv[1])
output_file = sys.argv[2]
output_type = sys.argv[3]

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
    
def fix_quotes(parent, quote_level = 0):
    for e in parent:
        if ab_ns('speaker') in e.attrib:
            del e.attrib[ab_ns('speaker')]
        if e.tag == html_ns('q'):
            fix_quotes(e, quote_level + 1)
            e.tag = html_ns('span')

            left = '“‘'[quote_level % 2]
            right = '”’'[quote_level % 2]

            if e.text:
                e.text = left + e.text
            else:
                e.text = left

            if e.get('class') == 'no-close-quote':
                del e.attrib['class']
            elif len(e):
                if e[-1].tail is None:
                    e[-1].tail = right
                else:
                    e[-1].tail += right
            else:
                e.text += right
        else:
            fix_quotes(e, quote_level)

ET.register_namespace('', ns['html'])
ET.register_namespace('ab', ns['ab'])
et = ET.parse('twir.xhtml')
fix_quotes(et.getroot())

content = get_content(et)

#for x, y in zip(content, range(len(content))):
#    print(y, x['title'])
html = et.find('.', ns)
title = et.find('./html:head/html:title', ns)
title.text += ', %s' % content[target_chapter]['title']

if output_type == 'web':
    nav = ET.Element('nav')
    if target_chapter > 0:
        prev = ET.SubElement(nav, 'a',
                             {'href': 'twir_%d.xhtml' % (target_chapter - 1)})
        prev.text = '« Prev'
        prev.tail = ' '
    select = ET.SubElement(nav, 'select',
                           {'id': 'nav-dropdown',
                            'onchange': '''\
var e = document.getElementById("nav-dropdown"); \
window.location.href = e.options[e.selectedIndex].value;\
'''})
    select.tail = ' '
    ET.SubElement(select, 'option', {'value': 'index.xhtml'}).text = 'Home'
    for chapter, number in zip(content, range(len(content))):
        option = ET.SubElement(select, 'option',
                               {'value': "twir_%s.xhtml" % number})
        option.text = chapter['title']
        if number == target_chapter:
            option.set('selected', 'true')
    if target_chapter < len(content) - 1:
        next = ET.SubElement(nav, 'a',
                             {'href': 'twir_%d.xhtml' % (target_chapter + 1)})
        next.text = 'Next »'
else:
    nav = None

# Remove existing body.
html.remove(et.find('./html:body', ns))

# Insert new body.
body = ET.SubElement(html, 'body')
if nav:
    body.append(nav)
body.extend(content[target_chapter]['content'])
if nav:
    body.append(nav)
et.write(output_file, encoding='UTF-8', xml_declaration=True)
