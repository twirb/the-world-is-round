all: spellcheck

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
	./check.py | LC_ALL=C sort -u > $@
dictionary: all-allowed all-forbidden
	LC_ALL=C comm -23 all-allowed all-forbidden > $@
all-allowed: common-words special-words
	LC_ALL=C sort -u $^ > $@
all-forbidden: forbidden-words
	perl -pe 's/^([^a-zA-Z]*)([a-z])/\1\u\2/' $< | cat - $< | \
	    LC_ALL=C sort -u > $@

clean:
	rm -f spellcheck bad-words words allowed-words all-allowed all-forbidden

.DELETE_ON_ERROR:
