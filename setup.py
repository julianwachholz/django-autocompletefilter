import os

from setuptools import find_packages, setup


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# Allow setup.py to be run from any directory
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

version = __import__('autocompletefilter').__version__

setup(
    name='django-autocompletefilter',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.4',
    install_requires=(
        'django>=2.0,<3.0',
    ),
    license='MIT',
    description='Django 2.0 ModelAdmin list_filter with autocomplete widget.',
    keywords='django django-admin autocomplete auto-complete filter select2',
    long_description=README,
    url='https://github.com/julianwachholz/django-autocompletefilter',
    author='Julian Wachholz',
    author_email='julian@wachholz.ch',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
