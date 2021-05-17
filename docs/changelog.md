# Changelog

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
