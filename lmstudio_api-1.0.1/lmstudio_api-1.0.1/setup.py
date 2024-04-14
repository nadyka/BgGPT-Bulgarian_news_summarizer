from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='lmstudio_api',
  version='1.0.1',
  description='AI api',
  long_description="lmstudio Official AI bot api",
  url='https://lmstudio.com',
  author='lmstudi0',
  author_email='yepmeagainplsnoban@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='lmstudio', 
  packages=find_packages(),
  install_requires=[]
)