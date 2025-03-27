# Changelog

### 1.1.2 - Bugfix and new packaging

- Fix branch coverage rate comparison when used with --branch without actual branches. Fixes
  [#23](https://github.com/smarie/python-genbadge/issues/23). PR
  [#37](https://github.com/smarie/python-genbadge/pull/37) by [marcegeek](https://github.com/marcegeek).
- Removed python 2.7, 3.5, 3.6 and 3.7 from CI. This version is the last where python versions < 3.8 are officially 
  supported.
- Refactored project layout so that tests are not packaged in wheel.
- `conda` is not the backend virtual environment anymore. Fixes [#35](https://github.com/smarie/python-genbadge/issues/35).

### 1.1.1 - Fixed support for latest Pillow and Python

- Fixed support for Python 3.12 by adding `setuptools` requirement explicitly. Fixed
  [#32](https://github.com/smarie/python-genbadge/issues/32).
- Fixed support for `Pillow` version 10 or greater. PR [#33](https://github.com/smarie/python-genbadge/pull/33) by
  [famura](https://github.com/famura).

### 1.1.0 - Option to change or remove the badge name

- A new `-n/--name` commandline option can be used with all badge generation commands to override the badge label (left text). A `--noname` commandline flag can alternatively be used to remove the left part completely. PR [#25](https://github.com/smarie/python-genbadge/pull/25) by [`nefrob`](https://github.com/nefrob).

### 1.0.6 - Bugfix

- Fixed the badge generator in "local" mode (badge created from local SVG template, not downloaded from shields.io). Fixes [#19](https://github.com/smarie/python-genbadge/issues/19). PR [#20](https://github.com/smarie/python-genbadge/pull/20) by [`texnofobix`](https://github.com/texnofobix).

### 1.0.5 - Bugfix

 - Removed dependency to `xunitparser` because its packaging relies on `use_2to3` which is not supported anymore in setuptools. Fixes [#18](https://github.com/smarie/python-genbadge/issues/18).

### 1.0.4 - Bugfix

 - `genbadge coverage`: fixed `ZeroDivisionError` when `coverage.xml` contains 0 branches (in particular when `--no-branch` option is set). Fixes [#15](https://github.com/smarie/python-genbadge/issues/15)

### 1.0.3 - technical release

 - `setup.py` is now using the contents of `setup.cfg` for download url and setuptools_scm. There is now a single configuration file. See [setuptools_scm#582](https://github.com/pypa/setuptools_scm/issues/582).

### 1.0.2 - technical release

 - Fixed the release message.

### 1.0.1 - bugfix - `defusedxml` import

 - `genbadge coverage` command: fixed `ImporError` with `defusedxml`. Fixed [#14](https://github.com/smarie/python-genbadge/issues/14).

### 1.0.0 - security patch + simplified tests badge

 - The tests badge now simplifies when the success rate is 100%, which is the case in the vast majority of projects. Fixes [#12](https://github.com/smarie/python-genbadge/issues/12)
   
 - Now using `defusedxml` to fix a [known vulnerability](https://docs.python.org/3/library/xml.etree.elementtree.html). Fixes [#11](https://github.com/smarie/python-genbadge/issues/11)

### 0.8.0 - New features

 - Added `flake8` command. Fixes [#3](https://github.com/smarie/python-genbadge/issues/3).
 - Added a "silent" flag `-s`. Fixes [#10](https://github.com/smarie/python-genbadge/issues/10)
 - Added a verbosity flag `-v`. Fixes [#1](https://github.com/smarie/python-genbadge/issues/1)
 - Python 3.9 is now officially supported. Fixes [#9](https://github.com/smarie/python-genbadge/issues/9)

### 0.7.1 - Bugfix

 - Fixed bug with writing to stdout. Fixed [#8](https://github.com/smarie/python-genbadge/issues/8).

### 0.7.0 - Badges can be written to stdout

 - Completed CLI help for subcommands. Fixes [#5](https://github.com/smarie/python-genbadge/issues/5)
 - Badges can now be redirected to `stdout` using `genbadge <cmd> -o -`. Fixes [#4](https://github.com/smarie/python-genbadge/issues/4)

### 0.6.0 - Added `coverage` command

 - New command `genbadge coverage` able to generate a badge from a `coverage.xml` coverage report

### 0.5.0 - First public version

 - Command group `genbadge` with global help
 - Command `genbadge tests` able to generate a badge from a `junit.xml` tests report, with :
   
    - color depending on success percentage (50%/75%/90%)
    - customization of input `junit.xml` file and output SVG badge file,
    - custom source (`shields.io` by default or local SVG file template for offline usage).
    - "fail on threshold" option to return an error code 1 when the success percentage is strictly lower than the threshold.
