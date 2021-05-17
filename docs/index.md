# genbadge

*Generate badges for tools that do not provide one.*

[![Python versions](https://img.shields.io/pypi/pyversions/genbadge.svg)](https://pypi.python.org/pypi/genbadge/) [![Build Status](https://github.com/smarie/python-genbadge/actions/workflows/base.yml/badge.svg)](https://github.com/smarie/python-genbadge/actions/workflows/base.yml) [![Tests Status](./reports/junit/junit-badge.svg?dummy=8484744)](./reports/junit/report.html) [![Coverage Status](./reports/coverage/coverage-badge.svg?dummy=8484744)](./reports/coverage/index.html) [![Flake8 Status](./reports/flake8/flake8-badge.svg?dummy=8484744)](./reports/flake8/index.html)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-genbadge/) [![PyPI](https://img.shields.io/pypi/v/genbadge.svg)](https://pypi.python.org/pypi/genbadge/) [![Downloads](https://pepy.tech/badge/genbadge)](https://pepy.tech/project/genbadge) [![Downloads per week](https://pepy.tech/badge/genbadge/week)](https://pepy.tech/project/genbadge) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-genbadge.svg)](https://github.com/smarie/python-genbadge/stargazers) [![codecov](https://codecov.io/gh/smarie/python-genbadge/branch/main/graph/badge.svg)](https://codecov.io/gh/smarie/python-genbadge)

`genbadge` provides a set of commandline utilities to generate badges for tools that do not provide one. It currently can create: 

 - [`tests`](#1-tests-badge) badges such as ![Tests Badge](./reports/junit/junit-badge.svg?dummy=8484744) from `pytest` or other `junit.xml`-generating framework,
 - [`coverage`](#2-coverage-badge) badges such as ![Coverage Badge](./reports/coverage/coverage-badge.svg?dummy=8484744) from python `coverage` or other `coverage.xml`-generating framework, 
 - [`flake8`](#3-flake8-badge) badges such as ![Flake8 Status](./reports/flake8/flake8-badge.svg?dummy=8484744) from `flake8 --statistics`. 

Badges are either generated using the [shields.io](https://shields.io/) HTTP REST API, or with an equivalent local SVG template included in `genbadge`.

## Installing

### Full

In order for all commandline features to work, you should install `genbadge` with the extra dependencies:

```bash
> pip install genbadge[all]
```

This is equivalent to `pip install genbadge[tests,coverage,flake8]`. Alternatively you can install dependencies for only a subset of commands for example `pip install genbadge[tests,flake8]`.

### Minimal

`genbadge` core only requires `click` (the CLI framework), `pillow` (for SVG file templating) and `requests` (to call the [shields.io](https://shields.io/) API). You can install it using

```bash
> pip install genbadge
```

This will only allow you to use the low-level [API](#4-low-level-api).

## Usage

Once installed, `genbadge` is available as a commandline utility. You can get some help with:

```bash
> genbadge

Usage: genbadge [OPTIONS] COMMAND [ARGS]...

  Commandline utility to generate badges. To get help on each command use:

      genbadge <cmd> --help

Options:
  --help  Show this message and exit.

Commands:
  coverage  Generate a badge for the coverage results (e.g. from a
            coverage.xml).%s
  flake8    Generate a badge for the flake8 results (e.g. from a flake8stats.txt
            file).%s
  tests     Generate a badge for the test results (e.g. from a junit.xml).

```


### 1. Tests badge

#### Prerequisite: a test report

##### a. `pytest`

If you use [`pytest`](https://docs.pytest.org), you can use some options to generate test reports:

 - with `--junitxml=path/to/junit.xml` a junit-format report is generated. This is the file that we'll need to generate the badge.

 - with `--html=path/to/report.html` a detailed HTML report is generated. This is not required to generate the badge, but you might wish to use it so that users navigate to it when they will click on your badge. 
   
!!! warning "Security concerns"
    Test reports might contain secrets (keys, env variables, OS user names containing employee numbers, etc.), so always review them carefully before publishing them !

Let's run this in your project:

```bash
> pytest --junitxml=reports/junit/junit.xml --html=reports/junit/report.html
```

You can check that the two files are correctly generated before moving forward.

##### b. Other frameworks

Any `junit.xml` input file would be accepted so other language users (e.g. java) can get this working for them as well.

#### Generating the badge

Now you can generate a badge similar to this one ![Tests Status](./reports/junit/junit-badge.svg?dummy=8484744) with the following command:

```bash
> genbadge tests
```

By default it assumes that

 - the input file can be found at `./reports/junit/junit.xml`. You can change this with the `-i/--input-file` flag. 
   
    - `-` can be used to denote `<stdin>`: e.g. `genbadge tests -i - < junit.xml`.

 - the output file will be at `./tests-badge.svg`. You can change it with the `-o/--output-file` flag

    - `-` can be used to denote `<stdout>`: e.g. `genbadge tests -o - > badge.svg`.

 - the badge should be generated using `shields.io` (requires an internet connection). If you prefer you can use `-l/--local` to use the included SVG file template (less mature but seems to work)

In addition to generating the badge, executing the command will also display some details about the parsed file is you use the verbose `-v` flag:

```bash
Test statistics parsed successfully from '(...)/reports/junit/junit.xml'
 - Nb tests: Total (6) = Success (2) + Skipped (1) + Failed (2) + Errors (1)
 - Success percentage: 40.00% (2 / 5) (Skipped tests are excluded)

SUCCESS - Tests badge created: '(...)/tests-badge.svg'
```

Note that without the verbose flag, only the last line of this message is displayed. You can disable it entirely using the silent flag `-s`.

The resulting badge will by default look like this: `[tests | 2/5]` where 2 is the number of tests that have run successfully, and 5 is the total number of tests *minus the number of skipped tests*. The success percentage, defined as this ratio multiplied by 100, is displayed and can be further used to fail on threshold, see [below](#failing-on-threshold).

Finally, the color of the badge depends on the success percentage.

 - Less than 50%: red
 - less than 75%: orange
 - less than 90%: green
 - higher: bright green


#### Using the badge

To include the resulting badge in your documentation and make it point to the generated `report.html`, you can for example use the following markdown:

`[![Tests Status](./reports/junit/junit-badge.svg?dummy=8484744)](./reports/junit/report.html)`

It will render as follows: [![Tests Status](./reports/junit/junit-badge.svg?dummy=8484744)](./reports/junit/report.html)

Note that the query part of the image url `?dummy=8484744` is a trick so that the github pages web server does not try to add an extra cache layer to the badge. Maybe this is not useful anymore with new versions of github, if you know the answer let me know !

!!! warning "Security concerns"
    Test reports might contain secrets (keys, env variables, OS user names containing employee numbers, etc.), so always review them carefully before publishing them !

#### Failing on threshold

You might wish the command to fail if the success percentage is not high enough.

This may be done using the `-t/--threshold` flag:

```bash
> genbadge tests -t 90
```

will fail and return an exit code of `1` if the success percentage is strictly lower than 90%.

The success percentage is defined as the number of tests that have run successfully, divided by the total number of tests *minus the number of skipped tests*, times 100. So for 6 tests run, if 2 tests ran successfully and 1 was skipped then the success percentage is `2 / (6 - 1) * 100` which gives `40%`.

### 2. Coverage badge

#### Prerequisite: a cov report

##### a. `coverage`

If you use [`coverage`](https://coverage.readthedocs.io), you can use some options to generate reports:

 - with `coverage report` the coverage statistics are displayed in the console. This is not required but might be useful to debug if the xml generation fails.

 - with `coverage xml` an XML-format report is generated. This is the file that we'll need to generate the badge.

 - with `coverage html` a detailed HTML report (a folder) is generated. This is not required to generate the badge, but you might wish to use it so that users navigate to it when they will click on your badge. 
   
Let's run this in your project:

```bash
> coverage report
> coverage xml
> coverage html
```

You can check that the coverage file and html report folder are correctly generated before moving forward.

##### b. Other frameworks

Any `coverage.xml` input file would be accepted so other language users (e.g. java) can get this working for them as well.

#### Generating the badge

Now you can generate a badge similar to this one ![Coverage Status](./reports/coverage/coverage-badge.svg?dummy=8484744) with the following command:

```bash
> genbadge coverage
```

By default it assumes that

 - the input file can be found at `./reports/coverage/coverage.xml`. You can change this with the `-i/--input-file` flag. 
   
    - `-` can be used to denote `<stdin>`: e.g. `genbadge coverage -i - < coverage.xml`.

 - the output file will be at `./coverage-badge.svg`. You can change it with the `-o/--output-file` flag

    - `-` can be used to denote `<stdout>`: e.g. `genbadge coverage -o - > badge.svg`.

 - the badge should be generated using `shields.io` (requires an internet connection). If you prefer you can use `-l/--local` to use the included SVG file template (less mature but seems to work)

In addition to generating the badge, executing the command will also display some details about the parsed file is you use the verbose `-v` flag:

```bash
Coverage results parsed successfully from '(...)/reports/coverage/coverage.xml'
 - Branch coverage: 5.56% (1/18)
 - Line coverage: 17.81% (13/73)
 - Total coverage: 15.38% ((1+13)/(18+73))

SUCCESS - Coverage badge created: '(...)/coverage-badge.svg'
```

Note that without the verbose flag, only the last line of this message is displayed. You can disable it entirely using the silent flag `-s`.

The resulting badge will by default look like this: `[coverage | 98.1%]` where 98.1 is the total coverage, obtained from the branch and line coverages using the formula `(nb_lines_covered + nb_branches_covered) / (nb_lines / nb_branches)` and multiplying this by 100.

Finally, the color of the badge depends on the success percentage.

 - Less than 50%: red
 - less than 75%: orange
 - less than 90%: green
 - higher: bright green


#### Using the badge

To include the resulting badge in your documentation and make it point to the generated HTML report, you can for example use the following markdown:

`[![Coverage Status](./reports/coverage/coverage-badge.svg?dummy=8484744)](./reports/coverage/index.html)`

It will render as follows: [![Coverage Status](./reports/coverage/coverage-badge.svg?dummy=8484744)](./reports/coverage/index.html)

Note that the query part of the image url `?dummy=8484744` is a trick so that the github pages web server does not try to add an extra cache layer to the badge. Maybe this is not useful anymore with new versions of github, if you know the answer let me know !


### 3. Flake8 badge

#### Prerequisite: a flake8 report

If you use [`flake8`](https://flake8.pycqa.org/), you can use some options to generate reports:

 - with `--statistics`, the number of issues grouped by code (e.g. `E201`) is consolidated and printed to std out. You can redirect this to a file named `flake8stats.txt` using `--tee --output-file flake8stats.txt`. This is the file that we'll need to generate the badge. Note that `--tee` is to continue to see the report on the console, this is optional.

 - with `--format=html --htmldir ` a detailed HTML report (a folder) is generated. This is not required to generate the badge, but you might wish to use it so that users navigate to it when they will click on your badge. 
   
Let's run this in your project. We use `--exit-zero` so that the commands always returns with exit code 0 even if problems are found.

```bash
> flake8 <src_folder> --exit-zero --format=html --htmldir ./reports/flake8 --statistics --tee --output-file flake8stats.txt
1     B014 Redundant exception types in `except (IOError, OSError):`.  Write `except OSError:`, which catches exactly the same exceptions.
7     C801 Copyright notice not present.
1     E122 continuation line missing indentation or outdented
1     E303 too many blank lines (3)
...
```

You can check that the statistics file and html report folder are correctly generated before moving forward.

#### Generating the badge

Now you can generate a badge similar to this one ![Flake8 Status](./reports/flake8/flake8-badge.svg) with the following command:

```bash
> genbadge flake8
```

By default it assumes that

 - the input file can be found at `./reports/flake8/flake8stats.txt`. You can change this with the `-i/--input-file` flag. 
   
    - `-` can be used to denote `<stdin>`: e.g. `genbadge flake8 -i - < flake8stats.txt`.

 - the output file will be at `./flake8-badge.svg`. You can change it with the `-o/--output-file` flag

    - `-` can be used to denote `<stdout>`: e.g. `genbadge flake8 -o - > badge.svg`.

 - the badge should be generated using `shields.io` (requires an internet connection). If you prefer you can use `-l/--local` to use the included SVG file template (less mature but seems to work)

In addition to generating the badge, executing the command will also display some details about the parsed file is you use the verbose `-v` flag:

```bash
Flake8 statistics parsed successfully from '(...)/reports/flake8/flake8stats.txt'
 - Total (20) = Critical (6) + Warning (9) + Info (5)

SUCCESS - Flake8 badge created: '(...)/flake8-badge.svg'
```

Note that without the verbose flag, only the last line of this message is displayed. You can disable it entirely using the silent flag `-s`.

The resulting badge will by default look like this: `[flake8 | 6 C, 0 W, 5 I]` where 6, 0, 5 denote the number of critical issues, warnings, and information messages respectively. These severity levels are determined by the `flake8-html` plugin so as to match the colors in the HTML report.

Finally, the color of the badge depends on the number of issues at each severity level.

 - at least a critical issue (severity 1): red
 - at least a warning (severity 2): orange
 - at least an info (severity 3): green
 - no issue at all: bright green


#### Using the badge

To include the resulting badge in your documentation and make it point to the generated HTML report, you can for example use the following markdown:

`[![Flake8 Status](./reports/flake8/flake8-badge.svg?dummy=8484744)](./reports/flake8/index.html)`

It will render as follows: [![Flake8 Status](./reports/flake8/flake8-badge.svg?dummy=8484744)](./reports/flake8/index.html)

Note that the query part of the image url `?dummy=8484744` is a trick so that the github pages web server does not try to add an extra cache layer to the badge. Maybe this is not useful anymore with new versions of github, if you know the answer let me know !

### 4. Low-level API

You can create a badge with the `Badge` class.

```python
from genbadge import Badge

b = Badge(left_txt="foo", right_txt="bar", color="green")
print(b)
```

yields

```
[ foo | bar ]  color: green
```

By default no svg is generated: this is a purely abstract badge. You can make it a real badge with the following code:

```python
b.write_to("tmp_badge.svg", use_shields=False)
```

Note the optional `use_shields` boolean flag that is used to switch between querying `shields.io` (`True`, default) or using a local SVG file template (`False`, but maybe less bullet-proof).


## See Also

Other badge generation projects exist:

 * [`coverage-badge`](https://github.com/dbrgn/coverage-badge), see in particular this [discussion](https://github.com/dbrgn/coverage-badge/issues/7)
 * [`flake8-svg-badge`](https://github.com/alex-rudakov/flake8-svg-badge) that seems abandoned ?


### Others

*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie/OVERVIEW#python)* 


## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-genbadge](https://github.com/smarie/python-genbadge)
