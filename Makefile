all: spellcheck twir.epub

PYTHON3 = python3
twir_%.xhtml: twir.xhtml split.py
	$(PYTHON3) split.py $(patsubst twir_%.xhtml,%,$(@F)) $@
toc.ncx: twir.xhtml toc.py toc-skeleton.xml
	$(PYTHON3) toc.py $@
epub/toc.ncx: toc.ncx

# This dependency list is the output of "git ls-files epub"
twir.epub: epub/META-INF/container.xml epub/content.opf			\
	epub/cover.jpg epub/icon.svg epub/mimetype			\
	epub/titlepage.xhtml epub/twir.css epub/twir_1.xhtml		\
	epub/twir_10.xhtml epub/twir_11.xhtml epub/twir_12.xhtml	\
	epub/twir_13.xhtml epub/twir_14.xhtml epub/twir_15.xhtml	\
	epub/twir_16.xhtml epub/twir_17.xhtml epub/twir_18.xhtml	\
	epub/twir_19.xhtml epub/twir_2.xhtml epub/twir_20.xhtml		\
	epub/twir_21.xhtml epub/twir_22.xhtml epub/twir_23.xhtml	\
	epub/twir_24.xhtml epub/twir_25.xhtml epub/twir_26.xhtml	\
	epub/twir_27.xhtml epub/twir_28.xhtml epub/twir_29.xhtml	\
	epub/twir_3.xhtml epub/twir_30.xhtml epub/twir_31.xhtml		\
	epub/twir_32.xhtml epub/twir_33.xhtml epub/twir_34.xhtml	\
	epub/twir_35.xhtml epub/twir_36.xhtml epub/twir_37.xhtml	\
	epub/twir_38.xhtml epub/twir_39.xhtml epub/twir_4.xhtml		\
	epub/twir_40.xhtml epub/twir_5.xhtml epub/twir_6.xhtml		\
	epub/twir_7.xhtml epub/twir_8.xhtml epub/twir_9.xhtml		\
	epub/twir_41.xhtml \
	epub/toc.ncx epub/f1.svg epub/f2.svg epub/f3.svg
	rm -f $@ && cd epub && zip --quiet ../twir.epub $(patsubst epub/%,%,$^)

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
	rm -f twir.epub toc.ncx
	rm -f twir_[0-9].xhtml twir_[0-9][0-9].xhtml

.DELETE_ON_ERROR:
