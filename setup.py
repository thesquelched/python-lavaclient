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


CHANGELOG_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'CHANGELOG.md')


def read_version():
    """Read the version from the lavaclient module"""
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'lavaclient',
        '_version.py'
    )
    with open(path) as f:
        exec(f.read())
        # Same as just returning __version__, but doesn't set off pyflakes
        return locals()['__version__']


def download_url():
    return (
        'https://github.com/rackerlabs/python-lavaclient/tarball/' +
        read_version()
    )


def long_description(changelog):
    return """\
`Package Documentation <http://python-lavaclient.readthedocs.org/en/latest>`_

`GitHub README <https://github.com/rackerlabs/python-lavaclient>`_

Changelog
---------

{changelog}
""".format(changelog=changelog)


if __name__ == '__main__':
    try:
        with open(CHANGELOG_PATH) as f:
            changelog = f.read().strip()
    except IOError:
        changelog = ''

    setup(
        name='lavaclient',
        version=read_version(),
        description='Client library for Rackspace Cloud Big Data API',
        long_description=long_description(changelog),
        license='Apache',

        author='Rackspace',
        url='https://github.com/rackerlabs/python-lavaclient',
        download_url=download_url(),

        packages=find_packages(exclude=['tests']),
        entry_points={
            'console_scripts': ['lava = lavaclient.cli:main'],
        },
        install_requires=[
            'python-keystoneclient>=1.3.0',
            'requests>=2.5.1',
            'six>=1.9.0',
            'python-dateutil>=2.4.2',
            'figgis>=1.6.2',
            'PySocks>=1.5.4',
        ],

        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Intended Audience :: Information Technology",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
            "Programming Language :: Python"
        ],
    )
