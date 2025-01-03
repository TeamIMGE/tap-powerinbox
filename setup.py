from setuptools import setup

setup(
    name="tap-powerinbox",
    version="0.1.0",
    description="Singer.io tap for extracting data from powerinbox",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_powerinbox"],
    install_requires=[
        "singer-python==5.4.1",
        "requests==2.32.2",
        'backoff==1.3.2',
    ],
    extras_require=[
        "ipdb==0.11",
        "pylint==1.9.4"
    ]
    entry_points="""
    [console_scripts]
    tap-powerinbox=tap_powerinbox:main
    """,
)
