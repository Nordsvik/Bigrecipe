from setuptools import find_packages, setup

setup(
    name="bigrecipe",
    version="0.9",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "flask-restful",
        "flask-sqlalchemy",
        "SQLAlchemy",
    ]
)
