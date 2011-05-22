PROJECT = asciitable
WWW = /proj/web-cxc-dmz/htdocs/contrib/$(PROJECT)

.PHONY: doc dist install

dist:
	rm -rf dist
	rm -f MANIFEST
	python setup.py sdist --format=zip
	python setup.py sdist --format=gztar

doc:
	cd doc; \
	make html

install: doc
	rsync -av doc/_build/html/ $(WWW)/

install_dev: doc dist
	rsync -av doc/_build/html/ $(WWW)/dev
	cp -p dist/$(PROJECT)-*.tar.gz $(WWW)/dev/downloads/
	cp -p dist/$(PROJECT)-*.tar.gz $(WWW)/dev/downloads/$(PROJECT).tar.gz

