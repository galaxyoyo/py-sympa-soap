import re

from setuptools import setup


with open("README.rst") as fh:
    long_description = re.sub(
        "^.. start-no-pypi.*^.. end-no-pypi", "", fh.read(), flags=re.M | re.S
    )

setup(
    name="sympasoap",
    version="1.0.0",
    description="A simple Python Sympa API",
    long_description=long_description,
    author="Yohann D'ANELLO",
    author_email="yohann.danello@animath.fr",
    url="https://gitlab.com/animath/si/py-sympa-soap",
    python_requires=">=3.6",
    install_requires=[
        "zeep~=1.4.0",
    ],
    tests_require=[],
    extras_require={},
    entry_points={},
    package_dir={"": "src"},
    packages=["sympasoap"],
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Development Status :: 2 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    zip_safe=False,
)
