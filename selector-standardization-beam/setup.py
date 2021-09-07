from setuptools import setup, find_packages

setup(
    name='selector-standardization-beam',
    version='0.4.14',
    description='Data Standardization pipeline in Apache Beam for Selector project',
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author='Nikita Zhiltsov',
    author_email='mail@codeforrussia.org',
    url='https://github.com/Code-for-Russia/selector-pipeline',
    packages=find_packages(where="src", exclude='test'),  # same as name
    package_dir={'': 'src'},
    install_requires=[
        'pytest>=6.2.4',
        'fastavro>=1.4.0',
        'apache-beam>=2.20.0',
        'selector-standardizers>=0.8.2'
    ],
    include_package_data=True,
    python_requires='>=3.7'
)