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
et = ET.parse('twir.xhtml')

html = et.find('.', ns)
body = et.find('./html:body', ns)
html.remove(body)
new_body = ET.SubElement(html, 'body')

cast_chap = ET.SubElement(new_body, 'h2')
cast_chap.text = "Cast"
cast_table = ET.SubElement(new_body, 'table')
head_tr = ET.SubElement(cast_table, 'tr')
character_td = ET.SubElement(head_tr, 'td')
character_td.text = "Character"
lines_td = ET.SubElement(head_tr, 'td')
lines_td.text = "Lines"

cast = {}
h2 = None
for e in body:
    if e.tag == html_ns('h2'):
        h2 = e
        continue

    quotes = e.findall('.//*[@ab:speaker]', ns)
    speaker = None
    filter = None
    p = None
    for quote in quotes:
        new_speaker = quote.attrib[ab_ns('speaker')]
        new_speaker = re.sub('\s+', ' ', new_speaker)
        new_filter = quote.get(ab_ns('filter'))
        if speaker == new_speaker and filter == new_filter:
            ellipsis = ET.SubElement(p, "span")
            ellipsis.text = " … "
        else:
            if h2 is not None:
                new_body.append(h2)
                h2 = None

            cast[new_speaker] = cast.get(new_speaker, 0) + 1
            p = ET.SubElement(new_body, 'p')
            if new_filter is None:
                p.text = "%s: " % new_speaker
            else:
                p.text = "%s (" % new_speaker
                em = ET.SubElement(p, 'em')
                em.text = new_filter
                em.tail = "): "
            speaker = new_speaker
            filter = new_filter

        quote.tail = None
        p.append(quote)

for k, v in sorted(cast.items(), key=lambda kv: (-kv[1], kv[0])):
    character_row = ET.SubElement(cast_table, 'tr')
    character_td = ET.SubElement(character_row, 'td')
    character_td.text = str(k)
    lines_td = ET.SubElement(character_row, 'td')
    lines_td.text = str(v)
    #print("%s: %s" % (k, v))

et.write('quotes.xml', encoding='UTF-8', xml_declaration=True)

