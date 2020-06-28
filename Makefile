all: spellcheck twir.epub

PYTHON3 = python3
epub/twir_%.xhtml: twir.xhtml split.py
	$(PYTHON3) split.py $(patsubst twir_%.xhtml,%,$(@F)) $@
epub/toc.ncx: twir.xhtml toc.py toc-skeleton.xml
	$(PYTHON3) toc.py $@

# This dependency list is the output of "git ls-files epub"

seq = 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 \
24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40
epub_files =					\
	$(patsubst %,twir_%.xhtml,$(seq))	\
	META-INF/container.xml			\
	content.opf				\
	f1.svg f2.svg f3.svg			\
	titlepage.xhtml				\
	toc.ncx					\
	twir.css
twir.epub: $(addprefix epub/,$(epub_files))
	rm -f $@ && cd epub && zip --quiet ../twir.epub $(epub_files)

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
	rm -f epub/twir_[0-9].xhtml epub/twir_[0-9][0-9].xhtml

.DELETE_ON_ERROR:
