help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  devel                      build and execute Fiano for development"
	@echo "  clean                      Great power involves great responsibility"
	@echo "  py-clean                   remove *.pyc files and __pycache__ files"
	@echo "  db-clean                   remove *.db files"
	@echo "Check the Makefile to know exactly what each target is doing."
	
devel:
	python3 fiano.py

.SILENT:
py-clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d | xargs rm -fr

.SILENT:
db-clean:
	find . -name '*.db' -delete

.SILENT:
clean:
	make py-clean 
	make db-clean