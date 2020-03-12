from setuptools import setup

setup(name='gitscmd',
      version='0.1',
      description='Run arbitrary commands on multiple git repos',
      long_description='gits runs git commands (or arbitrary commands) on a set of git repositories defined in a .gits file',
      classifiers=[
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.6',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'Topic :: Software Development :: Version Control :: Git',
            'Topic :: Utilities',
      ],
      url='http://github.com/yaunj/gitscmd',
      author='Rune Hammersland',
      author_email='rune@hammersland.net',
      license='MIT',
      packages=['gitscmd'],
      entry_points={
            'console_scripts': ['gits=gitscmd.gits_cli:main'],
      },
      zip_safe=False)
