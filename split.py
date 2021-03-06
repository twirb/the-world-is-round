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
    if tag == html_ns("br"):
        yield " "

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

def fix_apostrophes(et):
    for e in et.find('.//html:body', ns).iter():
        if e.text is not None:
            e.text = e.text.replace("'", "’")
        if e.tail is not None:
            e.tail = e.tail.replace("'", "’")

def fix_chapter_numbers(et):
    for e in et.findall('.//html:h2/html:div', ns):
        e.tag = 'span'
        e.text += ': '

def remove_ab(et):
    for e in et.iter():
        for key in list(e.keys()):
            if key.startswith('{%s}' % ns['ab']):
                del e.attrib[key]

def remove_icon(et):
    head = et.find('.//html:head', ns)
    icon = head.find('./html:link[@rel="icon"]', ns)
    head.remove(icon)

def convert_img(et):
    for e in et.findall('.//html:img', ns):
        e.attrib["src"] = e.attrib["src"].replace('svg', 'png')

ET.register_namespace('', ns['html'])
ET.register_namespace('ab', ns['ab'])
et = ET.parse('twir.xhtml')
if output_type == 'epub':
    fix_quotes(et.getroot())
    fix_chapter_numbers(et)
    remove_icon(et)
    remove_ab(et)
    convert_img(et)
fix_apostrophes(et.getroot())

content = get_content(et)

#for x, y in zip(content, range(len(content))):
#    print(y, x['title'])
html = et.find('.', ns)
title = et.find('./html:head/html:title', ns)
title.text += ', %s' % content[target_chapter]['title']

def nav(which):
    dropdown_id = 'nav-dropdown-%s' % which
    nav = ET.Element('nav')
    if target_chapter > 0:
        prev = ET.SubElement(nav, 'a',
                             {'href': 'twir_%d.xhtml' % (target_chapter - 1)})
        prev.text = '« Prev'
        prev.tail = ' '
    select = ET.SubElement(nav, 'select',
                           {'id': dropdown_id,
                            'onchange': '''\
var e = document.getElementById("''' + dropdown_id + '''"); \
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
    return nav

# Remove existing body.
html.remove(et.find('./html:body', ns))

# Insert new body.
body = ET.SubElement(html, 'body')
if output_type == 'web':
    body.append(nav('top'))
body.extend(content[target_chapter]['content'])
if output_type == 'web':
    body.append(nav('bottom'))
et.write(output_file, encoding='UTF-8', xml_declaration=True)
