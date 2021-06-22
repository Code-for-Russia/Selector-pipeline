from setuptools import setup, find_packages

setup(
    name='selector-standardization-flow',
    version='0.2',
    description='Selector Pipeline Standardization',
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author='Nikita Zhiltsov',
    author_email='mail@codeforrussia.org',
    url='https://github.com/Code-for-Russia/selector-pipeline',
    packages=find_packages(exclude='test'),  # same as name
    install_requires=[
        'pytest>=6.2.4',
        'fastavro>=1.4.0',
        'apache-airflow>=2.0.2',
        'apache-beam>=2.26.0',
        'apache-airflow-providers-apache-beam>=2.0.0',
        'apache-airflow-providers-google>=2.0.0'
    ],
    include_package_data=True,
    python_requires='>=3.7'
)