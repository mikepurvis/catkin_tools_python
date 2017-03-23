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
import os
import re
import subprocess
import sys


DESCRIPTION = 'Iterate a bin directory, looking for scripts with python shebangs to replace.'


def get_arg_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('bindir', metavar='BIN', type=str,
                        help='Path to search.')
    parser.add_argument('-p', '--python', metavar='PYTHON', type=str,
                        help='Replacement shebang.', default='/usr/bin/env python')
    return parser


def fix_shebangs(bin_dir, python_exec):
    modified_files = 0
    if os.path.isdir(bin_dir):
        for bin_file in os.listdir(bin_dir):
            with open(os.path.join(bin_dir, bin_file)) as f:
                first_line = f.readline(100)
                if not first_line.startswith('#!') or 'python' not in first_line:
                    # Either an actual binary, or a non-python shebang.
                    continue
                new_first_line = '#!' + python_exec + '\n'
                if new_first_line == first_line:
                    # Existing shebang already matches expected.
                    continue
                rest_of_file = f.read()
            with open(os.path.join(bin_dir, bin_file), 'w') as f:
                f.write(new_first_line + rest_of_file)
            modified_files += 1
    return modified_files


def main():
    args = get_arg_parser().parse_args()
    ret = fix_shebangs(args.bindir, args.python)
    if ret:
        print "Modified %s script(s) found in [%s]" % (ret, args.bindir)
    else:
        print "No scripts modified in [%s]" % args.bindir
