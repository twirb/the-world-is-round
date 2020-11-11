# The World is Round

This is a repository for the novel "The World is Round", a 1978 science fiction
novel by Tony Rothman (https://www.tonyrothman.com/about), with Tony's
permission.  It contains the full text of the novel in [one HTML
file](twir.xhtml), plus scripts for breaking it into chapter-per-file HTML for
easy online reading and for converting it to EPUB and MOBI formats for
e-readers.

If you just want to read the novel, visit https://twirb.github.io/, which has it
in all of the formats listed above.  If you want to run the scripts yourself,
perhaps because you want to submit a pull request to fix a typo, or because you
want to convert it to a different format, you will need to install the following
tools, in addition to the core utilities normally present on a GNU/Linux system:

* GNU make (https://www.gnu.org/software/make/).

* Python version 3.x (https://www.python.org/).

* The "convert" program from ImageMagick (https://imagemagick.org/), to convert
  the diagrams from SVG to PNG format.

* The "zip" program from Info-ZIP (http://infozip.sourceforge.net/) to produce
  the EPUB file.

* Optionally, EPUBCheck (https://github.com/w3c/epubcheck) available to run as
  "epubcheck", to ensure that the generated EPUB file is valid.

* The "ebook-convert" program from Calibre (https://calibre-ebook.com/) to
  convert the EPUB to MOBI format.

The following targets are available:

* `all` (the default target): Runs everything below.

* `spellcheck`: Checks spelling, and for a couple of other kinds of errors, in
  `twirb.xhtml` against the dictionaries in `common-words` and `special-words`.
  If there are any errors, this tries to print them in context on stdout, but
  look in `bad-words` for more information.

* `twir.epub`: The EPUB format.

* `twir.mobi`: The MOBI format.

* `web`: The website content with all of the formats it includes, under the
  `web/` directory.

* `twir.zip`: A zip of the website content.
