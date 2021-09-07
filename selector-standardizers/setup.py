from setuptools import setup, find_packages

setup(
    name='selector-standardizers',
    version='0.8.2',
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
        'org.codeforrussia.selector.standardizer.schemas.regional': ['*.avsc'],
        'org.codeforrussia.selector.standardizer.schemas.municipal': ['*.avsc'],
        'org.codeforrussia.selector.standardizer.schemas': ['*.json'],
                  },
    install_requires=[
        'pytest>=6.2.4',
        'fastavro>=1.4.0',
        'jsonlines>=2.0.0',
        'dataclasses>=0.6',
        'sentence_transformers>=1.2.0',
        'scikit-learn>=0.24.2',
        'google-cloud-storage>=1.38.0',
    ],
    include_package_data=True,
    python_requires='>=3.7'
)