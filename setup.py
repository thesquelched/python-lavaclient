# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from setuptools import setup, find_packages
import os.path


REQUIREMENTS_TXT = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'requirements.txt')


def requirements():
    try:
        with open(REQUIREMENTS_TXT) as f:
            return f.readlines()
    except IOError:
        return []


def read_version():
    """Read the version from the lavaclient2 module"""
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'lavaclient2',
        '__init__.py'
    )
    with open(path) as f:
        exec(f.read())
        # Same as just returning __version__, but doesn't set off pyflakes
        return locals()['__version__']


if __name__ == '__main__':
    setup(
        name='python-lavaclient',
        version=read_version(),
        author='Rackspace',
        description='Client library for Rackspace Cloud Big Data API',

        packages=find_packages(exclude=['tests']),
        install_requires=[],

        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Intended Audience :: Information Technology",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
            "Programming Language :: Python"
        ],
    )
