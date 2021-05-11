# genbadge

*Generate badges for tools that do not provide one.*

[![Python versions](https://img.shields.io/pypi/pyversions/genbadge.svg)](https://pypi.python.org/pypi/genbadge/) [![Build Status](https://github.com/smarie/python-genbadge/actions/workflows/base.yml/badge.svg)](https://github.com/smarie/python-genbadge/actions/workflows/base.yml) [![Tests Status](./reports/junit/junit-badge.svg?dummy=8484744)](./reports/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-genbadge/branch/main/graph/badge.svg)](https://codecov.io/gh/smarie/python-genbadge)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-genbadge/) [![PyPI](https://img.shields.io/pypi/v/genbadge.svg)](https://pypi.python.org/pypi/genbadge/) [![Downloads](https://pepy.tech/badge/genbadge)](https://pepy.tech/project/genbadge) [![Downloads per week](https://pepy.tech/badge/genbadge/week)](https://pepy.tech/project/genbadge) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-genbadge.svg)](https://github.com/smarie/python-genbadge/stargazers)

`genbadge` provides a set of commandline utilities to generate badges for tools that do not provide one. It currently includes support for `tests` (`pytest` or other `junit.xml`-generating framework), `coverage` and `flake8`. 

Badges are either generated using the [shields.io](https://shields.io/) HTTP REST API, or with an equivalent local SVG template.

## Installing

### Full

In order for all comandline features to work, you should install `genbadge` with the extra dependencies:

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
  tests  Generate a badge for the test results (e.g. from a junit.xml).

```


### 1. Tests badge

#### Prerequisite: a test report

##### a. `pytest`

If you use `pytest`, you can use some options to generate test reports:

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

Now you can generate a badge similar to this one [![Tests Status](./reports/junit/junit-badge.svg?dummy=8484744)](./reports/junit/report.html) with the following command:

```bash
> genbadge tests
```

By default it assumes that

 - the input file can be found at `./reports/junit/junit.xml`. You can change this with the `-i/--input-file` flag. 
   
    - `-` can be used to denote `<stdin>`: e.g. `genbadge tests -i - < junit.xml`.

 - the output file will be at `./tests-badge.svg`. You can change it with the `-o/--output-file` flag

 - the badge should be generated using `shields.io` (requires an internet connection). If you prefer you can use `-l/--local` to use the included SVG file template (less mature but seems to work)

In addition to generating the badge, executing the command will also display some messages:

```bash
Test statistics parsed successfully from '(...)/reports/junit/junit.xml'
 - Nb tests: Total (6) = Success (2) + Skipped (1) + Failed (2) + Errors (1)
 - Success percentage: 40.00% (2 / 5) (Skipped tests are excluded)

SUCCESS - Tests badge created: '(...)/tests-badge.svg'
```

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

TODO

### 3. Flake8 badge

TODO

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
 * [`flake8-svg-badge`](https://github.com/alex-rudakov/flake8-svg-badge) that seems abandoned


### Others

*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie/OVERVIEW#python)* 


## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-genbadge](https://github.com/smarie/python-genbadge)
