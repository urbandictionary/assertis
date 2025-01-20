# assertis

assertis is a command-line tool and Python library for comparing directories of images. It's designed to verify that changes to image-generating code produce the expected results.

assertis compares a directory of "expected" images against a directory of "actual" images, highlighting any differences it finds. It can detect added, removed, and changed images, and can generate visual diffs to show exactly what has changed in each image.

Key features:
- Compare directories of images
- Generate HTML reports with visual diffs
- Adjustable sensitivity for image comparisons
- Command to automatically update expected images
- Web interface for viewing comparison results

# Installation

`pip install --force-reinstall -U git+https://github.com/urbandictionary/assertis`

# Python API

assertis can also be used as a Python library:

```python
from assertis import compare, ComparisonException

try:
    compare(
        expected_dir="path/to/expected",
        actual_dir="path/to/actual",
        report_dir="path/to/report",  # optional, will use temp dir if not specified
        sensitivity=0  # optional, defaults to 0
    )
except ComparisonException as e:
    # The comparison failed - differences were found
    print(str(e))  # Will contain the report details
```

The `compare()` function will:
1. Compare the images in the directories
2. Generate a report in the specified directory (or a temp directory)
3. Raise a `ComparisonException` if there are any differences
4. The exception message contains a formatted report of the differences
