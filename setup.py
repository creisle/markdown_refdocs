from setuptools import find_packages, setup

# Dependencies required to use your package
INSTALL_REQS = ['typing_extensions>=3.7.4.2']

# Dependencies required only for running tests
TEST_REQS = ['pytest', 'pytest-runner', 'pytest-cov']

# Dependencies required for deploying to an index server
DEPLOYMENT_REQS = ['twine', 'wheel']

DOC_REQS = ['mkdocs', 'mkdocs-material']

DEV_REQS = (
    TEST_REQS + DEPLOYMENT_REQS + DOC_REQS + ['black', 'flake8', 'flake8-annotations', 'mypy']
)

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
    version='1.3.0',
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
    package_data={'markdown_refdocs': ['py.typed']},
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
