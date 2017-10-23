from setuptools import setup

setup(name='aws_utilties',
      version='0.1',
      description='Useful scripts',
      url='https://github.com/rexc/aws_utilities',
      author='Rex Chan',
      author_email='rex.chan@originenergy.com.au',
      license='MIT',
      packages=['scripts'],
      entry_points={
          'console_scripts': ['assume_role=scripts.assume_role:main', 'subnets=scripts.networks:print_subnets'],
      },
      zip_safe=False)
