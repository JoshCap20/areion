from setuptools import setup, find_packages

setup(
    name="Areion",
    version="0.1.0",
    author="Josh Caponigro",
    author_email="joshcaponigro@gmail.com",
    description="A lightweight, fast, and extensible Python web server framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/joshcap20/areion",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "jinja2",
        "apscheduler",
    ],
)
