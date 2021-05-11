# Changelog

### 0.5.0 - First public version

 - Command group `genbadge` with global help
 - Command `genbadge tests` able to generate a badge from a junit.xml tests report, with 
   
    - color depending on success percentage (50%/75%/90%)
    - customization of input `junit.xml` file and output SVG badge file,
    - custom source (`shields.io` by default or local SVG file template for offline usage).
    - "fail on threshold" option to return an error code 1 when the success percentage is strictly lower than the threshold.
