from setuptools import setup, find_packages
import re

with open("requirements.txt", "r") as f:
    requirements_raw = f.read().splitlines()

# Parse requirements to make them more flexible
requirements = []
for req in requirements_raw:
    # Convert specific versions to minimum versions for core packages
    if re.match(r'^(numpy|Pillow|moviepy|scipy|scikit-image|scikit-learn|opencv-python).*$', req):
        name = req.split('==')[0] if '==' in req else req.split('>=')[0]
        requirements.append(f"{name}")
    else:
        requirements.append(req)

setup(
    name="batch_image_processor",
    version="0.1",
    package_dir={"": "python/src"},
    packages=find_packages(where="python/src"),
    install_requires=requirements,
    python_requires='>=3.8',
)