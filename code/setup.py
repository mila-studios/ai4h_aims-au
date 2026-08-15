import re

import setuptools

version_file_path = "qut01/_version.py"
version_regex_pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
with open(version_file_path) as fd:
    match_output = re.search(version_regex_pattern, fd.read(), re.M)
version_str = match_output.group(1)

setuptools.setup(
    name="qut01",
    version=version_str,
    description="QUT01 AI Against Modern Slavery (AIMS) Project Package",
    author="plstcharles",
    author_email="pierreluc.stcharles@mila.quebec",
        url="https://github.com/mila-studios/ai4h_aims-au",
    install_requires=["lightning", "hydra-core"],
    packages=setuptools.find_packages(),
)
