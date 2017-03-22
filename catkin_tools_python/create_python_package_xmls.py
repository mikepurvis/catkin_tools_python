# Copyright 2017 Clearpath Robotics Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import em
import os
from pkginfo import UnpackedSDist
import re
import subprocess
import sys
from tempfile import mkdtemp

from catkin_tools_python import filters


PACKAGE_XML_TEMPLATE = '''<?xml version="1.0"?>
<package format="2">
  <name>@(filters.name(pkginfo.name))</name>
  <version>@(filters.version(pkginfo.version))</version>
  <description>@(pkginfo.summary)</description>
@[if pkginfo.maintainer and pkginfo.maintainer_email]@
  <maintainer email="@(pkginfo.maintainer_email)">@(pkginfo.maintainer)</maintainer>
@[else]@
  <maintainer email="@(pkginfo.author_email)">@(pkginfo.author)</maintainer>
@[end if]@
  <license>@(pkginfo.license or 'Unknown')</license>

  <buildtool_depend>python</buildtool_depend>

@[for dep_name, dep_comparison, dep_version in dependencies]@
@[if dep_comparison]@
  <exec_depend @(filters.comparisons[dep_comparison])="@(filters.version(dep_version))">@(filters.name(dep_name))</exec_depend>
@[else]@
  <exec_depend>@(filters.name(dep_name))</exec_depend>
@[end if]@
@[end for]@

  <export><build_type>python</build_type></export>
</package>
'''

DESCRIPTION = 'Walk a source workspace, looking for paths containing a ' + \
    'PKG-INFO file but not a package.xml file. When found, create an ' + \
    'appropriate package.xml file in those paths.'


def get_arg_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('roots', metavar='ROOT', type=str, nargs='*',
                        help='Path to begin searching in.', default=['src'])
    return parser


def create_package_xmls(root_dir):
    if not os.path.exists(root_dir):
        print('Path [%s] does not exist, ignoring.' % root_dir)
        return
    egg_dir = mkdtemp()
    for d in os.listdir(root_dir):
        pkg_dir = os.path.join(root_dir, d)
        if os.path.exists(os.path.join(pkg_dir, 'PKG-INFO')):
            pkginfo = UnpackedSDist(pkg_dir)
            requires_file = os.path.join(pkg_dir, '%s.egg-info' % pkginfo.name, 'requires.txt')

            # If the egg-info directory is missing from the sdist archive, generate it here.
            if not os.path.exists(requires_file):
                try:
                    subprocess.check_output(['python', 'setup.py', 'egg_info', '-e', egg_dir],
                                             cwd=pkg_dir, stderr=subprocess.STDOUT)
                    requires_file = os.path.join(egg_dir, '%s.egg-info' % pkginfo.name, 'requires.txt')
                except subprocess.CalledProcessError:
                    # Super old distutils packages (like pyyaml) don't support egg_info.
                    pass

            # Parse through the egg-info/requires.txt file to determine package dependencies.
            dependencies = []
            if os.path.exists(requires_file):
                with open(requires_file) as f:
                    for depline in f.readlines():
                        if depline.startswith('['):
                            # We don't care about dependencies for docs, testing, etc.
                            break
                        m = re.match('([a-zA-Z0-9_-]*)\s*([<>=]*)\s*([a-zA-Z0-9_.-]*)', depline)
                        if m and m.group(1):
                            dependencies.append(m.groups())

            # Generate a package.xml file for this package.
            package_xml_path = os.path.join(root_dir, d, 'package.xml')
            if os.path.exists(package_xml_path):
                print('Exists:  %s' % package_xml_path)
            else:
                with open(package_xml_path, 'w') as f:
                    f.write(em.expand(PACKAGE_XML_TEMPLATE, {
                        'pkginfo': pkginfo,
                        'filters': filters,
                        'dependencies': dependencies
                        }))
                print('Created: %s' % package_xml_path)


def main():
    args = get_arg_parser().parse_args()
    for root in args.roots:
        create_package_xmls(root)
