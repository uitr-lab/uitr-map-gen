from setuptools import setup, find_packages

setup(
    name='uitr-map-gen',
    version='0.1.8',
    description='quick hex/grid/square/polygon map generators for interactive histogram maps',
    author='Nick Blackwell',
    author_email='nick.blackwell@ubc.ca',
    packages=find_packages(),  # Automatically finds all packages
    install_requires=[
        "geopandas>=1.0.1", "pyproj>=3.7.1", "pandas>=2.2.3", "openpyxl>=3.1.5",
    ],
    python_requires='>=3.11',
    include_package_data=True,
)