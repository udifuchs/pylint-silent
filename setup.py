"""pylint-silent Setup script."""
from typing import Dict, Any
import setuptools

with open("README.md", "r") as file_in:
    long_description = file_in.read()

main_ns: Dict[str, Any] = {}
# version_path = convert_path('pylint_silent/version.py')
with open("pylint_silent/version.py") as version_file:
    exec(version_file.read(), main_ns)  # pylint: disable=exec-used

setuptools.setup(
    name="pylint-silent",
    version=main_ns['__version__'],
    author="Udi Fuchs",
    author_email="udifuchs@gmail.com",
    license="GPLv2+",
    url="http://github.com/udifuchs/pylint-silent",
    description="Automatically add code comments to silence the output of pylint",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["pylint_silent"],
    entry_points={
        "console_scripts": [
            "pylint-silent = pylint_silent.__main__:main",
        ],
    },
    classifiers=[
        "Topic :: Software Development :: Quality Assurance",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.6",
    keywords=["pylint"],
)
