# Docstring Extractor

Note: currently only supports google-style docstrings. May add support for others later if requested.

Yet another docstring extraction pacakge. The motivation for this package was that writing docs in
markdown is simpler to read and write than writing them in RST. There is an awesome package called
[Mkdocs](https://www.mkdocs.org/) for turning your markdown documents into a static site. It has a
number of plugins which extract docstrings from python files, however none of them
are able to use the google docstring format which I prefer. If you're using a different docstring
format you can check them out here on the [Mkdocs plugin wiki](https://github.com/mkdocs/mkdocs/wiki/MkDocs-Plugins#api-documentation-building).

## Features

- parses google-style docstrings
- generates markdown output (this allows the user to link into the navigation or their main docs)
- can take package directories as input
- reads type annotations
- pulls function signatures

## Getting Started

Install the package from pip

```bash
pip install docstring_extractor
```

Run this from the command line or import the function to get the markdown returns as strings and
customize. This tool has the customary help manu you can view with the `-h` option to see the
options documentation

```bash
docstring_extractor -h
```



