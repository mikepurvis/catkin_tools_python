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

mapping = {
    'PIL': 'python-imaging',
    'pyserial': 'python-serial',
    'PyYAML': 'python-yaml',
    'dxfgrabber': 'dxfgrabber',
    'progressbar2': 'python-progressbar'
}

comparisons = {
    '>=': 'version_gte',
    '>': 'version_gt',
    '=': 'version_eq',
    '<=': 'version_lte',
    '<': 'version_lt'
}

def name(name):
    return mapping.get(name,
            'python-' + name.lower().replace('_', '-'))

def version(version):
    version_parts = version.split('.')
    version_parts += ['0'] * (3 - len(version_parts))
    return '.'.join(version_parts)


