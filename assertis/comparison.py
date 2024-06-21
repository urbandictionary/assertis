import filecmp
import json
import os
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

from assertis.file_utils import glob
from assertis.image_comparison import compare_images
from assertis.md5_utils import md5_hash, md5_hash_image
from assertis.models import AddedFile, ChangedFile, DeletedFile, Report, UnchangedFile
from assertis.write import generate_html_report, write_report


def md5_path(path):
    return f"{md5_hash(path)}{path.suffix}"


def run_comparison(expected, actual, sensitivity):
    "Run the comparison between expected and actual directories."
    expected_dir = Path(expected)
    actual_dir = Path(actual)

    report = Report()

    expected_paths = glob(expected_dir)
    actual_paths = glob(actual_dir)

    for path in expected_paths:
        if path not in actual_paths:
            report.files.append(
                DeletedFile(
                    expected_md5=md5_hash(expected_dir / path),
                    name=str(path),
                    reasons=["Image deleted"],
                )
            )

    for path in actual_paths:
        expected_path = expected_dir / path
        actual_path = actual_dir / path

        if path not in expected_paths:
            report.files.append(
                AddedFile(
                    actual_file=md5_path(actual_path),
                    actual_md5=md5_hash(actual_path),
                    name=str(path),
                    reasons=["Image added"],
                )
            )
            report.outputs[str(md5_path(actual_path))] = actual_path
        else:
            if filecmp.cmp(expected_path, actual_path, shallow=False):
                report.files.append(
                    UnchangedFile(
                        actual_file=md5_path(actual_path),
                        actual_md5=md5_hash(actual_path),
                        expected_file=md5_path(expected_path),
                        expected_md5=md5_hash(expected_path),
                        name=str(path),
                        reasons=["Image unchanged"],
                    )
                )
                report.outputs[md5_path(actual_path)] = actual_path
            else:
                identical, diff_image, reasons = compare_images(
                    expected_path, actual_path, sensitivity
                )
                if identical:
                    report.files.append(
                        UnchangedFile(
                            actual_file=md5_path(actual_path),
                            expected_file=md5_path(expected_path),
                            md5_actual=md5_hash(actual_path),
                            md5_expected=md5_hash(expected_path),
                            name=str(path),
                            reasons=["Image unchanged"],
                        )
                    )
                    report.outputs[md5_path(actual_path)] = actual_path
                else:
                    diff_file = None
                    if diff_image:
                        md5_hash_value = md5_hash_image(diff_image)
                        diff_file = f"{md5_hash_value}.png"
                        report.outputs[diff_file] = diff_image
                    report.files.append(
                        ChangedFile(
                            actual_file=md5_path(actual_path),
                            actual_md5=md5_hash(actual_path),
                            diff_file=diff_file,
                            expected_file=md5_path(expected_path),
                            expected_md5=md5_hash(expected_path),
                            name=str(path),
                            reasons=reasons,
                        )
                    )
                    report.outputs[md5_path(actual_path)] = actual_path
                    report.outputs[md5_path(expected_path)] = expected_path
    report.files.sort(key=lambda item: item.name)
    return report


def write_comparison(expected, actual, report_dir, sensitivity):
    report = run_comparison(expected, actual, sensitivity)
    write_report(report, Path(report_dir))
    return report
