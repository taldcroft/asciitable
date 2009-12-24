PROJECT = asciitable
WWW = /proj/web-cxc/htdocs/contrib/$(PROJECT)

.PHONY: doc dist install

dist:
	python setup.py sdist

doc:
	cd doc; \
	make html

install: doc dist
	rsync -av doc/_build/html/ $(WWW)/
	rsync -av dist/$(PROJECT)-*.tar.gz $(WWW)/downloads/

