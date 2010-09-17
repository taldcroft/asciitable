PROJECT = asciitable
WWW = /proj/web-cxc/htdocs/contrib/$(PROJECT)

.PHONY: doc dist install

dist:
	rm -rf dist
	python setup.py sdist

doc:
	cd doc; \
	make html

install: doc dist
	rsync -av doc/_build/html/ $(WWW)/
	cp -p dist/$(PROJECT)-*.tar.gz $(WWW)/downloads/
	cp -p dist/$(PROJECT)-*.tar.gz $(WWW)/downloads/$(PROJECT).tar.gz

install_dev: doc dist
	rsync -av doc/_build/html/ $(WWW)/dev
	cp -p dist/$(PROJECT)-*.tar.gz $(WWW)/dev/downloads/
	cp -p dist/$(PROJECT)-*.tar.gz $(WWW)/dev/downloads/$(PROJECT).tar.gz

