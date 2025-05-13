from setuptools import setup, find_packages

setup(
    name="cricket_parser",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pydantic>=2.6.1",
        "python-dateutil>=2.8.2",
    ],
    python_requires=">=3.12",
) 