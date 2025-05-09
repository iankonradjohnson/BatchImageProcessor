from setuptools import setup, find_packages
import re
import sys

print(f"Using Python {sys.version}")

with open("requirements.txt", "r") as f:
    requirements_raw = f.read().splitlines()
    
print(f"Read {len(requirements_raw)} requirements from requirements.txt")

# Create a new, sanitized requirements list
requirements = []
dependency_links = []

# Hard requirements that should NOT have version constraints
problematic_packages = [
    'alabaster', 'sphinx', 'matplotlib', 'contourpy', 'networkx', 'tifffile',
    'numpy', 'pillow', 'moviepy', 'scipy', 'scikit-image', 'scikit-learn', 
    'opencv-python', 'pytorch-lightning', 'torch', 'torchvision', 
    'sphinxcontrib-applehelp', 'sphinxcontrib-devhelp', 'sphinxcontrib-htmlhelp',
    'sphinxcontrib-jsmath', 'sphinxcontrib-qthelp', 'sphinxcontrib-serializinghtml'
]

# Add these specific problematic packages without version constraints
for pkg in problematic_packages:
    requirements.append(pkg)

# Process the requirements.txt file for other dependencies
for req in requirements_raw:
    # Skip comments and empty lines
    if req.startswith('#') or not req.strip():
        continue
    
    # Handle editable installs separately
    if req.startswith('-e '):
        dependency_links.append(req.replace('-e ', ''))
        if '#egg=' in req:
            package_name = req.split('#egg=')[1]
            # Don't add to requirements if it's already there
            if package_name.lower() not in [r.lower() for r in requirements]:
                requirements.append(package_name)
        continue
        
    # Extract package name
    if '==' in req:
        package_name = req.split('==')[0].strip().lower()
    elif '>=' in req:
        package_name = req.split('>=')[0].strip().lower()
    elif '<' in req:
        package_name = req.split('<')[0].strip().lower()
    else:
        package_name = req.strip().lower()
    
    # Skip if this package is already in our problematic packages list
    if package_name in [p.lower() for p in problematic_packages]:
        continue
    
    # Add this requirement
    requirements.append(req)

# Print for debug
print(f"Processed {len(requirements)} requirements")

setup(
    name="batch_image_processor",
    version="0.1",
    package_dir={"": "python/src"},
    packages=find_packages(where="python/src"),
    install_requires=requirements,
    dependency_links=dependency_links,
    python_requires='>=3.8',
)