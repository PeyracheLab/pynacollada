# -*- coding: utf-8 -*-
# @Author: gviejo
# @Date:   2022-01-17 13:34:41
# @Last Modified by:   gviejo
# @Last Modified time: 2022-01-17 13:58:34
from setuptools import setup, find_packages

with open('README.md') as readme_file:
	readme = readme_file.read()


requirements = [
	'pynapple',
	'scikit-learn'
]

test_requirements = []

setup(
    author="Guillaume Viejo",
    author_email='guillaume.viejo@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description='Collaborative platform for high-level analysis with pynapple',
    install_requires=requirements,
    license="GNU General Public License v3",
    # long_description='pynapple is a Python library for analysing neurophysiological data. It allows to handle time series and epochs but also to use generic functions for neuroscience such as tuning curves and cross-correlogram of spikes. It is heavily based on neuroseries.' 
    # + '\n\n' + history,
    long_description=readme,
    include_package_data=True,
    keywords='neuroscience',
    name='pynacollada',
    # packages=find_packages(include=['pynacollada', 'pynacollada.*']),
    packages=['pynacollada'],
    url='https://github.com/PeyracheLab/pynacollada',
    version='v0.1.0',
    zip_safe=False,
    long_description_content_type='text/markdown'
    # download_url='https://github.com/PeyracheLab/pynapple/archive/refs/tags/v0.2.0-alpha.0.tar.gz'
)
