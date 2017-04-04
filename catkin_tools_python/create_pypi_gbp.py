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
import shutil
import subprocess
import tempfile
import yaml

DESCRIPTION = 'Sets up the tracks.yaml file to import and patch a PyPI package.'

template = yaml.load('''
tracks:
  indigo:
    actions:
    - mkdir -p :{archive_dir_path}/:{name}-:{version}
    - wget ...
    - tar -xvf :{archive_dir_path}/upstream.tar.gz -C :{archive_dir_path}/:{name}-:{version}
      --strip-components 1
    - create_python_package_xmls --pkgdir :{archive_dir_path}/:{name}-:{version} --version :{version}
    - tar -cvzf :{archive_dir_path}/:{name}-:{version}.tar.gz -C :{archive_dir_path}/:{name}-:{version}
      .
    - git-bloom-import-upstream :{archive_dir_path}/:{name}-:{version}.tar.gz
    - git-bloom-generate -y rosrelease :{ros_distro} --source upstream -i :{release_inc}
    devel_branch: null
    last_version: None
    name: upstream
    patches: null
    release_inc: '0'
    release_repo_url: null
    release_tag: :{ask}
    ros_distro: indigo
    vcs_type: tar
    vcs_uri: None
    version: :{ask}
''')

def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('pkg', metavar='PKG', type=str,
                        help='PyPI package name.')
    parser.add_argument('url', metavar='URL', type=str,
                        help='Path or URL to a GBP git repo.')
    parser.add_argument('-t', '--track', metavar='TRACK', type=str, default='indigo',
                        help='Track name to use.')
    args = parser.parse_args()

    pkg_normalized = args.pkg.lower().replace('_', '-')

    wget_line = 'wget https:://files.pythonhosted.org/packages/source/%s/%s/%s-:{release_tag}.tar.gz -O :{archive_dir_path}/upstream.tar.gz' % \
        (pkg_normalized[0], pkg_normalized, args.pkg)
    template['tracks']['indigo']['actions'][1] = wget_line

    tempdir = tempfile.mkdtemp()

    try:
        subprocess.check_output(['git', 'clone', args.url, tempdir])

        with open(os.path.join(tempdir, 'tracks.yaml'), 'w') as f:
            f.write(yaml.dump(template, default_flow_style=False))

        subprocess.check_output(['git', 'add', 'tracks.yaml'],
                                cwd=tempdir)
        if (subprocess.call(['git', 'commit', '-m', 'Add tracks.yaml'],
                            cwd=tempdir) == 0):
            subprocess.check_output(['git', 'push', 'origin', 'master'],
                                    cwd=tempdir)
        else:
            print "No change to tracks.yaml."

    finally:
        shutil.rmtree(tempdir)
