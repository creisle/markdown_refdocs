# Markdown Refdocs

![build](https://github.com/creisle/markdown_refdocs/workflows/build/badge.svg) [![PyPi](https://img.shields.io/pypi/v/markdown_refdocs.svg)](https://pypi.org/project/markdown-refdocs) [![codecov](https://codecov.io/gh/creisle/markdown_refdocs/branch/master/graph/badge.svg)](https://codecov.io/gh/creisle/markdown_refdocs) ![PyPI - Downloads](https://img.shields.io/pypi/dm/markdown_refdocs)

Extracts docstings and type annotations from a python package to generate reference documentation in markdown.
See an example of this at: https://creisle.github.io/markdown_refdocs/

## Getting Started

Install the package from pip

```bash
pip install markdown_refdocs
```

Run this from the command line or import the function to get the markdown returns as strings and
customize. This tool has the customary help manu you can view with the `-h` option to see the
options documentation

```bash
markdown_refdocs -h
```

Generate markdown reference documentation from your python package like so

```bash
markdown_refdocs /path/to/python/package -o /path/to/output/dir
```

This will generate markdown files under `/path/to/output/dir` which can
be used standalone or incorporated in a [Mkdocs](https://www.mkdocs.org/) build

## Examples

Documentation for this package itself can be generated using this tool itself

```bash
markdown_refdocs markdown_refdocs -o docs/reference
```

This will build the following files (1 file per python sub-module)

```text
docs/reference/
└── markdown_refdocs
    ├── links.md
    ├── main.md
    ├── markdown.md
    ├── parsers.md
    └── types.md
```

See a live demo of this under: https://creisle.github.io/markdown_refdocs

## Features

- parses google-style docstrings
- generates markdown output (this allows the user to link into the navigation or their main docs)
- can take package directories as input
- reads type annotations
- pulls function signatures

## Limitations

- currently only supports [google-style docstrings](http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings). May add support for others later if requested.

## Motivation

The motivation for this package was that writing docs in
markdown is simpler to read and write than writing them in RST. There is an awesome package called
[Mkdocs](https://www.mkdocs.org/) for turning your markdown documents into a static site. It has a
number of plugins which extract docstrings from python files, however none of them
are able to use the google docstring format which I prefer. If you're using a different docstring
format you can check them out here on the [Mkdocs plugin wiki](https://github.com/mkdocs/mkdocs/wiki/MkDocs-Plugins#api-documentation-building).
