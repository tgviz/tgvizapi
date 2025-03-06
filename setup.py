from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tgviz",
    version="0.1.2",
    description="Universal asynchronous library for posting Telegram Updates to TGViz API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="TGVIZ",
    author_email="tgvizapi@gmail.com",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.23.0",
        "pydantic>=1.8.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
