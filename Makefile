all: spellcheck twir.epub epubcheck twir.zip

PYTHON3 = python3

chapter_numbers := $(shell seq 0 42)

## ------- ##
## webpage ##
## ------- ##

web_files_nodir = \
	$(patsubst %,twir_%.xhtml,0 $(chapter_numbers)) \
	cover.png f1.svg f2.svg f3.svg equation.png 	\
	index.xhtml twir.css twir.epub twir.xhtml
web_files = $(addprefix web/,$(web_files_nodir))
web/twir_%.xhtml: twir.xhtml split.py
	$(PYTHON3) split.py $(patsubst twir_%.xhtml,%,$(@F)) $@ web
web/index.xhtml: twir.xhtml toc.py index-skeleton.xhtml
	$(PYTHON3) toc.py $@ web
web/twir.epub: twir.epub
web: $(web_files)

twir.zip: $(web_files)
	rm -f $@ && cd web && zip --quiet ../twir.zip $(web_files_nodir)

## ---- ##
## epub ##
## ---- ##
epub_files =						\
	mimetype \
	$(patsubst %,twir_%.xhtml,$(chapter_numbers))	\
	META-INF/container.xml				\
	content.opf					\
	cover.png					\
	icon.svg f1.png f2.png f3.png equation.png 	\
	titlepage.xhtml					\
	toc.ncx						\
	twir.css
twir.epub: $(addprefix epub/,$(epub_files))
	rm -f $@ && cd epub && zip --quiet -X ../twir.epub $(epub_files)

epub/twir_%.xhtml: twir.xhtml split.py
	$(PYTHON3) split.py $(patsubst twir_%.xhtml,%,$(@F)) $@ epub
epub/toc.ncx: twir.xhtml toc.py toc-skeleton.xml
	$(PYTHON3) toc.py $@ epub
epub/%.png: %.svg
	convert -density 400 $< $@

epubcheck: twir.epub
	if (epubcheck -version 2>/dev/null | grep -q EPUBCheck); then \
		epubcheck twir.epub; \
	else \
		echo "epubcheck not installed, skipping check"; \
	fi && touch $@

## ------------- ##
## Spellchecking ##
## ------------- ##
spellcheck: bad-words
	@if test -s bad-words; then \
		grep -F -n -w --color=auto -f bad-words twir.xhtml /dev/null; \
		echo "Potential spelling errors above.  Fix them one of the following ways:"; \
		echo "- Fix actual spelling errors in 'twir.xhtml'."; \
		echo "- Add common dictionary words to 'common-words'."; \
		echo "- Add special vocabulary to 'special-words'."; \
		echo "(Run 'make' in a terminal to highlight error candidates'."; \
		echo "See 'bad-words' for a list of the words highlighted above."; \
		exit 1; \
	else \
		: > $@; \
	fi
bad-words: words dictionary
	LC_ALL=C comm -23 words dictionary > $@
words: twir.xhtml check.py
	$(PYTHON3) check.py | LC_ALL=C sort -u > $@
dictionary: all-allowed all-forbidden
	LC_ALL=C comm -23 all-allowed all-forbidden > $@
all-allowed: common-words special-words
	LC_ALL=C sort -u $^ > $@
all-forbidden: forbidden-words
	perl -pe 's/^([^a-zA-Z]*)([a-z])/\1\u\2/' $< | cat - $< | \
	    LC_ALL=C sort -u > $@

clean:
	rm -f spellcheck bad-words words dictionary all-allowed all-forbidden
	rm -f twir.epub epub/toc.ncx
	rm -f web/index.xhtml
	rm -f web/twir_[0-9].xhtml web/twir_[0-9][0-9].xhtml
	rm -f epub/twir_[0-9].xhtml epub/twir_[0-9][0-9].xhtml
	rm -f epubcheck

.DELETE_ON_ERROR:
