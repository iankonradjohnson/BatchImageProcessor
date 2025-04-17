from setuptools import setup, find_namespace_packages

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="batch_image_processor",
    version="0.1",
    package_dir={"": "python/src"},
    packages=find_namespace_packages(where="python/src"),
    install_requires=requirements,
)
