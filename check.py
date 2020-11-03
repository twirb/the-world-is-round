#! /usr/bin/python3
import xml.etree.ElementTree as ET
import re
tree = ET.parse('twir.xhtml')

ns = {'html': "http://www.w3.org/1999/xhtml",
      'ab': "http://example.org/audiobook-schema"}

def html_ns(tag):
    return "{%s}%s" % (ns['html'], tag)
def ab_ns(tag):
    return "{%s}%s" % (ns['ab'], tag)

allowed = {}
def allow_html(tag, attributes=()):
    assert html_ns(tag) not in allowed
    allowed[html_ns(tag)] = set(attributes)

ab_attributes = (ab_ns("speaker"), ab_ns("filter"))
style_attributes = ("class",)
allow_html("html",
           (('{http://www.w3.org/XML/1998/namespace}lang',
             '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation')))
allow_html("title")
allow_html("head")
allow_html("meta", (('name', 'content')))
allow_html("link", (('rel', 'href')))
allow_html("a", (('href',)))
allow_html("style")
allow_html("body")
allow_html("h1")
allow_html("h2", (('id',)))
allow_html("h3")
allow_html("p", style_attributes + ab_attributes)
allow_html("blockquote", ab_attributes)
allow_html("div", style_attributes + ab_attributes)
allow_html("span", style_attributes + ab_attributes)
allow_html("q", style_attributes + ab_attributes)
allow_html("i", ab_attributes)
allow_html("b")
allow_html("em", ab_attributes)
allow_html("strong", ab_attributes)
allow_html("hr")
allow_html("table")
allow_html("tr")
allow_html("td")
allow_html("sup")
allow_html("img", (('src', 'alt', 'title', 'width')))
allow_html("br")

def handle_element(node):
    if node.tag in allowed:
        allowed_attrs = allowed[node.tag]
        for k in node.keys():
            if k not in allowed_attrs:
                print("tag %s has disallowed attribute %s" % (node.tag, k))
    else:
        print("bad tag %s" % node.tag)
    for child in node:
        handle_element(child)
        
def itermosttext(element):
    tag = element.tag
    if not isinstance(tag, str) and tag is not None:
        return
    if tag == html_ns("style"):
        return

    t = element.text
    if t:
        yield t
    for e in element:
        yield from itermosttext(e)
        t = e.tail
        if t:
            yield t

handle_element(tree.getroot())

word_re = re.compile(r'[+–\s​—–−…*=()]+')
for text in itermosttext(tree.getroot()):
    for word in word_re.split(text):
        word = word.rstrip('.!?,;:')
        if len(word):
            print(word)
