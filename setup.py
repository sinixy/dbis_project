from setuptools import setup

setup(
    name='kpi_network',
    packages=['kpi_network'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-migrate',
        'flask-cors',
        'python-dotenv',
    ],
)