import os

from setuptools import setup


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(os.path.dirname(__file__), requirements_file),
              'r') as f:
        requirements = f.read().splitlines()
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]


extra_files = package_files('lingua_franca')

setup(
    name='lingua_franca',
    version='0.1',
    packages=['test', 'lingua_franca', 'lingua_franca.lang'],
    url='https://github.com/MycroftAi/lingua_franca',
    license='Apache2.0',
    package_data={'': extra_files},
    include_package_data=True,
    install_requires=required('requirements.txt'),
    author='jarbasAI',
    author_email='jarbasai@mailfence.com',
    description='Mycroft\'s multilingual text parsing and formatting library'
)
