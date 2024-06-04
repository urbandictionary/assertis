# assertis

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
