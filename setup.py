from setuptools import setup, find_packages

# Dependencies required to use your package
INSTALL_REQS = []

# Dependencies required only for running tests
TEST_REQS = ['pytest', 'pytest-runner', 'pytest-cov']

# Dependencies required for deploying to an index server
DEPLOYMENT_REQS = ['twine', 'wheel']

DOC_REQS = ['mkdocs', 'mkdocs-material']

DEV_REQS = TEST_REQS + DEPLOYMENT_REQS + DOC_REQS + ['black', 'flake8', 'flake8-annotations']

long_description = ''

try:
    import os

    with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as fh:
        long_description = fh.read()
except Exception as err:
    print(err)
    pass

setup(
    name='markdown_refdocs',
    version='1.0.1',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=INSTALL_REQS,
    extras_require={
        'dev': DEV_REQS,
        'deploy': DEPLOYMENT_REQS,
        'test': TEST_REQS,
        'docs': DOC_REQS,
    },
    python_requires='>=3.6',
    author_email='caralynreisle@gmail.com',
    author='Caralyn Reisle',
    dependency_links=[],
    test_suite='tests',
    tests_require=TEST_REQS,
    entry_points={
        'console_scripts': ['markdown_refdocs = markdown_refdocs.main:command_interface']
    },
    url='https://github.com/creisle/markdown_refdocs',
)
