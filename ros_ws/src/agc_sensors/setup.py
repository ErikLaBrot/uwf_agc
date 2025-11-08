from setuptools import setup

package_name = 'agc_sensors'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/gps_compass.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Erik LaBrot',
    maintainer_email='erik.labrot@uwf.edu',
    description='ROS2 nodes for AGC sensor interfaces (GPS + Compass)',
    license='MIT',
    entry_points={
        'console_scripts': [
            'gps_compass = agc_sensors.gps_compass_node:main',
        ],
    },
)
