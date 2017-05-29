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
import shutil
import subprocess
import sys
from tempfile import mkdtemp
import logging
import pprint

from catkin_tools_python import filters

# fix for em unicode handling
em.str = unicode
em.Stream.write_old = em.Stream.write
em.Stream.write = lambda self, data: em.Stream.write_old(self, data.encode('utf8'))

PACKAGE_XML_TEMPLATE = '''<?xml version="1.0"?>
<package format="2">
  <name>@(filters.name(pkginfo.name))</name>
  <version>@(version_override or filters.version(pkginfo.version))</version>
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
@[for system_dep_name in system_dependencies]@
  <exec_depend>@(system_dep_name)</exec_depend>
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
                        help='Path to begin searching in.')
    parser.add_argument('--pkgdir', metavar='DIR', type=str,
                        help='Only one package, in this directory. If specified, no roots may be given.')
    parser.add_argument('--version', metavar='VERSION', type=str,
                        help='Version string to use, defaults to setup.py version.')
    parser.add_argument('--deps', metavar='PKGS', type=str, nargs='*',
                        help='Extra dependencies to include in package.xml', default=[])
    parser.add_argument('--debug', action='store_true', help="Turn on debugging")
    return parser


def create_one_package_xml(pkg_dir, version_override=None, system_dependencies=[]):
    logging.debug("create_one_packages_xml: pkg_dir %s:" % pkg_dir)
    pkginfo = UnpackedSDist(pkg_dir)

    # default value for requires.txt
    requires_file = os.path.join(pkg_dir, '%s.egg-info' % pkginfo.name, 'requires.txt')

    # see if there is an egg-info directory in the pkg_dir
    for listing in os.listdir(pkg_dir):
        if 'egg-info' in listing:
            requires_file = os.path.join(pkg_dir, listing, 'requires.txt')
            logging.debug("create_one_packages_xml: requires_file : %s" % requires_file)

    # If the egg-info directory is missing from the sdist archive, generate it here.
    egg_dir = None
    if not os.path.exists(requires_file):
        logging.debug("create_one_packages_xml: requires_file does not exist try to generate it")
        try:
            egg_dir = mkdtemp()
            subprocess.check_output(['python', 'setup.py', 'egg_info', '-e', egg_dir],
                                    cwd=pkg_dir, stderr=subprocess.STDOUT)
            logging.debug("create_one_packags_xml: generating new egg directory ")
            requires_file = os.path.join(egg_dir, '%s.egg-info' % pkginfo.name, 'requires.txt')
        except subprocess.CalledProcessError:
            # Super old distutils packages (like pyyaml) don't support egg_info.
            pass

    # Parse through the egg-info/requires.txt file to determine package dependencies.
    dependencies = []
    logging.debug("Requires file: %s" % requires_file)
    if os.path.exists(requires_file):
        with open(requires_file) as f:
            for depline in f.readlines():
                depline = depline.rstrip()
                logging.debug("Processing %s" % depline)
                if depline.startswith('['):
                    logging.debug("Doc/testing dependency %s -- no more dependency needed breaking from loop" % depline)
                    # We don't care about dependencies for docs, testing, etc.
                    break
                # match the dependency and the version if one is given, version is optional
                m = re.match('([a-zA-Z0-9_-]*)\s*([<>=]*)\s*([a-zA-Z0-9_.-]*)', depline)
                if m and m.group(1):
                    logging.debug("Adding %s to the dependency list" % m.group(1))
                    dependencies.append(m.groups())

    logging.debug("Dependencies %s" % pprint.pformat(dependencies))
    if egg_dir:
        shutil.rmtree(egg_dir)

    # Generate a package.xml file for this package.
    package_xml_path = os.path.join(pkg_dir, 'package.xml')
    if os.path.exists(package_xml_path):
        print('Exists:  %s' % package_xml_path)
    else:
        logging.debug("Writing package.xml file with the template contents")

        with open(package_xml_path, 'w') as f:
            f.write(em.expand(PACKAGE_XML_TEMPLATE, {
                'pkginfo': pkginfo,
                'filters': filters,
                'dependencies': dependencies,
                'system_dependencies': system_dependencies,
                'version_override': version_override
                }))
        print('Created: %s' % package_xml_path)


def create_package_xmls(root_dir):
    if not os.path.exists(root_dir):
        print('Path [%s] does not exist, ignoring.' % root_dir)
        return
    for d in os.listdir(root_dir):
        pkg_dir = os.path.join(root_dir, d)
        if os.path.exists(os.path.join(pkg_dir, 'PKG-INFO')):
            create_one_package_xml(pkg_dir)


def main():
    args = get_arg_parser().parse_args()

    # enable debugging
    LOGLEVEL = "DEBUG" if args.debug else None
    logging.basicConfig(level=LOGLEVEL)

    if args.roots and args.pkgdir:
        print("Only specify roots or --pkgdir, not both.")
        sys.exit(1)
    if args.pkgdir:
        create_one_package_xml(args.pkgdir, args.version, args.deps)
    else:
        if args.version or args.deps:
            print "Can't use --version or --deps when processing multiple packages."
            sys.exit(1)
        for root in args.roots:
            create_package_xmls(root)
