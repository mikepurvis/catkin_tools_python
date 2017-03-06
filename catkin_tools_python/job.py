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

import os
import pkginfo

from catkin_tools.jobs.cmake import copy_install_manifest
from catkin_tools.jobs.cmake import generate_env_file
from catkin_tools.jobs.cmake import generate_setup_file
from catkin_tools.jobs.cmake import get_python_install_dir

from catkin_tools.jobs.utils import copyfiles
from catkin_tools.jobs.utils import loadenv
from catkin_tools.jobs.utils import makedirs
from catkin_tools.jobs.utils import rmfiles

from catkin_tools.execution.jobs import Job
from catkin_tools.execution.stages import CommandStage
from catkin_tools.execution.stages import FunctionStage


def create_python_build_job(context, package, package_path, dependencies, force_cmake, pre_clean):

    # Package source space path
    pkg_dir = os.path.join(context.source_space_abs, package_path)

    # Package build space path
    build_space = context.package_build_space(package)

    # Package metadata path
    metadata_path = context.package_metadata_path(package)

    # Environment dictionary for the job, which will be built
    # up by the executions in the loadenv stage.
    job_env = dict(os.environ)

    # Get actual staging path
    dest_path = context.package_dest_path(package)
    final_path = context.package_final_path(package)

    # Create job stages
    stages = []

    # Load environment for job.
    stages.append(FunctionStage(
        'loadenv',
        loadenv,
        locked_resource='installspace',
        job_env=job_env,
        package=package,
        context=context
    ))

    # Create package metadata dir
    stages.append(FunctionStage(
        'mkdir',
        makedirs,
        path=metadata_path
    ))

    # Copy source manifest
    stages.append(FunctionStage(
        'cache-manifest',
        copyfiles,
        source_paths=[os.path.join(context.source_space_abs, package_path, 'package.xml')],
        dest_path=os.path.join(metadata_path, 'package.xml')
    ))

    # Python setup install
    stages.append(CommandStage(
        'build',
        ['/usr/bin/env', 'python', 'setup.py',
         'build', '--build-base', build_space],
        cwd=pkg_dir
    ))

    # Python setup install
    stages.append(CommandStage(
        'install',
        ['/usr/bin/env', 'python', 'setup.py',
         'build', '--build-base', build_space,
         'install', '--old-and-unmanageable', '--prefix', dest_path],
        cwd=pkg_dir,
        locked_resource='installspace'
    ))

    # Determine the location where the setup.sh file should be created
    stages.append(FunctionStage(
        'setupgen',
        generate_setup_file,
        context=context,
        install_target=dest_path
    ))

    stages.append(FunctionStage(
        'envgen',
        generate_env_file,
        context=context,
        install_target=dest_path
    ))

    return Job(
        jid=package.name,
        deps=dependencies,
        env=job_env,
        stages=stages)


def create_python_clean_job(context, package, package_path, dependencies, dry_run,
                            clean_build, clean_devel, clean_install):
    stages = []

    # Package build space path
    build_space = context.package_build_space(package)

    # Package metadata path
    metadata_path = context.package_metadata_path(package)

    # Environment dictionary for the job, empty for a clean job
    job_env = {}

    stages = []

    return Job(
        jid=package.name,
        deps=dependencies,
        env=job_env,
        stages=stages)
