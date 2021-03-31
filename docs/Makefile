# Minimal makefile for Sphinx documentation
#
#export SPHINX_APIDOC_OPTIONS=members,no-undoc-members,no-show-inheritance
export SPHINX_APIDOC_OPTIONS=members

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


buildapi:

	rm -f source/_modules/*
	sphinx-apidoc -fMeET --templatedir=source/_templates -o source/_modules ../bci_framework
	jupyter nbconvert --to rst source/notebooks/readme.ipynb
	jupyter nbconvert --to markdown source/notebooks/readme.ipynb --output ../../../README.md

	python fix_readme.py