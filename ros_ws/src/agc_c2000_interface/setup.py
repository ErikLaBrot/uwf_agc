from setuptools import setup
import os
from glob import glob

package_name = 'agc_c2000_interface'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        # <-- THIS line installs the package marker into the ament index
        ('share/ament_index/resource_index/packages',
         [os.path.join('resource', package_name)]),

        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/c2000_tx.launch.py']),
    ],
    install_requires=['setuptools','pyserial'],
    zip_safe=True,
    maintainer='You',
    maintainer_email='you@example.com',
    description='Ultra-simple serial interface to C2000 MCU',
    license='MIT',
    entry_points={
        'console_scripts': [
            'c2000_tx = agc_c2000_interface.c2000_tx:main',
        ],
    },
)
