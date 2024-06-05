from setuptools import setup, find_packages

setup(
    name="assertis",
    version="0.1.0",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
        "click",
        "Pillow",
        "pydantic",
        "jinja2",
        "watchdog",
    ],
    entry_points={
        "console_scripts": [
            "assertis=assertis.cli:assertis"
        ],
    },
    package_data={
        "": ["report_template.html"],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for comparing and serving image comparison reports.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/assertis",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
