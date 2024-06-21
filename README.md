# assertis

## What is assertis?

assertis is a command-line tool for comparing directories of images. It's designed to help developers and testers verify that changes to image-generating code produce the expected results. assertis compares a directory of "expected" images against a directory of "actual" images, highlighting any differences it finds. It can detect added, removed, and changed images, and can generate visual diffs to show exactly what has changed in each image.

Key features:
- Compare directories of images
- Generate HTML reports with visual diffs
- Adjustable sensitivity for image comparisons
- Command to automatically update expected images
- Web interface for viewing comparison results

`pip install --force-reinstall -U git+https://github.com/urbandictionary/assertis`

# Test cases

| Test Case Directory            | Description                                                                                   |
|--------------------------------|-----------------------------------------------------------------------------------------------|
| files_added                    | Only the `actual` directory contains a file, and the `expected` directory is empty.           |
| files_removed                  | Only the `expected` directory contains a file, and the `actual` directory is empty.           |
| files_unchanged                | Both `actual` and `expected` directories contain identical files.                             |
| files_changed                  | Both `actual` and `expected` directories contain the same photo, but the `actual` file has added text. |
| lots_of_files                  | Both `actual` and `expected` directories contain multiple files, and they are identical, except that half of the actuals have added text. |
| files_changed_size             | Both `actual` and `expected` directories contain files of the same image, but the `actual` file has been resized. |
| files_changed_mode             | Both `actual` and `expected` directories contain files of the same PNG image, but the `actual` file has a different mode (RGBA). |
| files_changed_lot.             | Both `actual` and `expected` directories contain the same photo, but the `actual` file has inverted colors. |
| empty                          | Both `actual` and `expected` directories are empty.                                           |
