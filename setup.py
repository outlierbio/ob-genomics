import setuptools

setuptools.setup(
    name="ob-genomics",
    version="0.1.0",
    url="https://github.com/outlierbio/ob-genomics",

    author="Jake Feala",
    author_email="jake@outlierbio.com",

    description="Pipelines and ETL for aggregating public genomics data",
    long_description=open('README.md').read(),

    packages=setuptools.find_packages(),

    install_requires=[
        'click',
        'luigi',
        'pandas',
        'PyYAML',
        'sqlalchemy'
    ],

    entry_points='''
        [console_scripts]
        ob-genomics=ob_genomics.cli:cli
    ''',

)
