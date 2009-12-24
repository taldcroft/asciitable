PROJECT = asciitable
WWW = /proj/web-cxc/htdocs/contrib/$(PROJECT)

.PHONY: docs dist install

dist:
	python setup.py sdist

docs:
	cd docs; \
	make html

install: docs dist
	rsync -av doc/_build/html/ $(WWW)/
	rsync -av dist/$(PROJECT)-*.tar.gz $(WWW)/downloads/

