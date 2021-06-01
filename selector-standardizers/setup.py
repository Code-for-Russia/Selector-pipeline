from setuptools import setup, find_packages

setup(
    name='selector-standardizers',
    version='0.1.0',
    description='Electoral Data Standardization classes for the Selector project',
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author='Nikita Zhiltsov',
    author_email='mail@codeforrussia.org',
    url='https://github.com/Code-for-Russia/selector-pipeline',
    packages=find_packages(where="src", exclude='test'),  # same as name
    package_dir={'': 'src'},
    package_data={
        'org.codeforrussia.selector.standardizer.schemas.common': ['*.avsc'],
        'org.codeforrussia.selector.standardizer.schemas.federal': ['*.avsc'],
                  },
    install_requires=[
        'pytest>=6.2.4',
        'fastavro>=1.4.0',
        'jsonlines>=2.0.0',
    ],
    include_package_data=True,
    python_requires='>=3.7'
)