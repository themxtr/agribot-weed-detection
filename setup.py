import os
from glob import glob
from setuptools import setup

package_name = 'weed_detector'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/weed_detector']),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='Weed detection robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'hello_node = weed_detector.hello_node:main',
            'yolo_detector_node = weed_detector.yolo_detector_node:main',
            'sprayer_node = weed_detector.sprayer_node:main',
            'fake_camera_node = weed_detector.fake_camera_node:main',
            'visualizer_node = weed_detector.visualizer_node:main',
            'field_patrol_node = weed_detector.field_patrol_node:main',
        ],
    },
)
