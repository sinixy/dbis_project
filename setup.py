from setuptools import setup

setup(
    name='KPI social network',
    packages=['app'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-migrate',
    ],
)