#!/usr/bin/env python

import argparse
import em
import os
from pkginfo import UnpackedSDist
import sys

from catkin_tools_python import filters


PACKAGE_XML_TEMPLATE = '''<?xml version="1.0"?>
<package format="2">
  <name>@(filters.name(p.name))</name>
  <version>@(filters.version(p.version))</version>
  <description>@(p.summary)</description>
@[if p.maintainer and p.maintainer_email]@
  <maintainer email="@(p.maintainer_email)">@(p.maintainer)</maintainer>
@[else]@
  <maintainer email="@(p.author_email)">@(p.author)</maintainer>
@[end if]@
  <license>@(p.license or 'Unknown')</license>

  <buildtool_depend>python</buildtool_depend>

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
    for d in os.listdir(root_dir):
        if os.path.exists(os.path.join(root_dir, d, 'PKG-INFO')):
            p = UnpackedSDist(os.path.join(root_dir, d))
            package_xml_path = os.path.join(root_dir, d, 'package.xml')
            if os.path.exists(package_xml_path):
                print('Exists:  %s' % package_xml_path)
            else:
                with open(package_xml_path, 'w') as f:
                    f.write(em.expand(PACKAGE_XML_TEMPLATE, { 'p': p, 'filters': filters }))
                print('Created: %s' % package_xml_path)


def main():
    args = get_arg_parser().parse_args()
    for root in args.roots:
        create_package_xmls(root)
