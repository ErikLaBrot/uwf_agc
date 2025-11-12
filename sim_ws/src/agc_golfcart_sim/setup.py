from setuptools import setup

package_name = 'agc_golfcart_sim'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='UWF AGC Team',
    maintainer_email='agc@uwf.edu',
    description='Gazebo simulation for UWF AGC autonomous golf cart',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'c2000_sim_bridge = agc_golfcart_sim.c2000_sim_bridge:main',
        ],
    },
)
