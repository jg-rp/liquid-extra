# pylint: disable=missing-module-docstring
import setuptools


with open("README.rst", "r", encoding="utf-8") as fd:
    long_description = fd.read()

setuptools.setup(
    name="python-liquid-extra",
    version="1.1.1",
    description="Extra tags an filters for python-liquid.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/jg-rp/liquid-extra",
    packages=setuptools.find_packages(exclude=["tests*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["python-liquid>=1.2.1"],
    test_suite="tests",
    python_requires=">=3.7",
    licence="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    project_urls={
        "Documentation": "https://jg-rp.github.io/liquid/extra/introduction",
        "Issue Tracker": "https://github.com/jg-rp/liquid-extra/issues",
        "Source Code": "https://github.com/jg-rp/liquid-extra",
        "Change Log": "https://github.com/jg-rp/liquid-extra/blob/main/CHANGES.rst",
    },
)
