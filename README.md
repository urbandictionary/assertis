# assertis

assertis is a command-line tool for comparing directories of images. It's designed to verify that changes to image-generating code produce the expected results.

assertis compares a directory of "expected" images against a directory of "actual" images, highlighting any differences it finds. It can detect added, removed, and changed images, and can generate visual diffs to show exactly what has changed in each image.

Key features:
- Compare directories of images
- Generate HTML reports with visual diffs
- Adjustable sensitivity for image comparisons
- Command to automatically update expected images
- Web interface for viewing comparison results

# Installation

`pip install --force-reinstall -U git+https://github.com/urbandictionary/assertis`