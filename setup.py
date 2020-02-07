from setuptools import setup

setup(
    name='catkin_tools_python',
    packages=['catkin_tools_python'],
    version='0.1.3',
    author='Mike Purvis',
    author_email='mike@uwmike.com',
    maintainer='Mike Purvis',
    maintainer_email='mike@uwmike.com',
    url='http://catkin-tools-python.readthedocs.org/',
    keywords=['catkin'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    description="Python buildtype plugin for catkin_tools.",
    long_description="Plugin for catkin_tools to build plain Python packages.",
    license='Apache 2.0',
    entry_points={
        'console_scripts': [
            'create_python_package_xmls = catkin_tools_python.create_python_package_xmls:main',
            'create_pypi_gbp = catkin_tools_python.create_pypi_gbp:main',
            'fix_python_script_shebangs = catkin_tools_python.fix_python_script_shebangs:main',
        ],
        'catkin_tools.jobs': [
            'python = catkin_tools_python:description',
        ]
    },
    install_requires=[
        'catkin_tools>=0.4.4',
        'empy',
        'pkginfo>=0.9.1'
    ]
)
