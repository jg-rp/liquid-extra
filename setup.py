import setuptools


with open("README.rst", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="python-liquid-extra",
    version="0.1.0",
    description="Extra tags an filters for python-liquid.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/jg-rp/liquid-extra",
    packages=setuptools.find_packages(exclude=["tests*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["python-liquid>=0.6.2"],
    test_suite="tests",
    python_requires=">=3.7",
)
