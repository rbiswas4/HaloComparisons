from distutils.core import setup

setup(# package information
      name="haloPropertyAnalysis",
      version="0.0.1dev",
      description='A set of utilities to analyze Halo mass function properties',
      long_description=''' ''',
      # What code to include as packages
      packages=['haloPropertyAnalysis'],
      package_dir={'haloPropertyAnalysis':'haloPropertyAnalysis'},
      # What data to include as packages
      include_package_data=True,
      package_data={'haloPropertyAnalysis': ['example_data/*']}
      )
