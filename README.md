catkin_tools_python
===================

This is a buildtype plugin for [catkin_tools][1] which allows building plain Python packages
as part of the isolated catkin workspace. Because catkin_tools is not able to see a package
or resolve dependencies without a `package.xml` file in the package directory, there is also
included a script which can be used before the build to spider the workspace, and create
the missing `package.xml` files for Python packages, based on the `PKG-INFO` file which is
standard with the Python sdist archive format.

[1]: https://catkin-tools.readthedocs.io


Demonstration
-------------

```
mkdir -p demo_ws/src && cd demo_ws
rosinstall_generator ros_base --deps --tar --rosdistro indigo > src/.rosinstall
curl https://gist.githubusercontent.com/mikepurvis/530df5cd34967f6a0aded2fea5c440db/raw/ros-base-python.yaml >> src/.rosinstall
wstool up -t src -j8
create_python_package_xmls src
catkin config --isolate-devel --merge-install --install
catkin build
```

When the build is complete, you can source the workspace and confirm that you are using the
libraries built into the workspace rather than your system copies:

```
source install/setup.bash
python -c 'import yaml; print yaml.__file__'
```

Note that this is just one of many possible workflows. If you don't want to generate the
`package.xml` files at build time as shown above, you could commit them along with the
upstream code into git repos, which would allow `rosdistro_build_cache` to cache them
and permit them to be resolved by `rosinstall_generator`.
