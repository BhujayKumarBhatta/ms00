from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='tokenleader',
      version='1.6',
      description='tokenleader server can be used by other microservices for token based  authentication and authorization',
      long_description=readme(),
      url='https://github.com/microservice-tsp-billing/tokenleader',
      author='Bhujay Kumar Bhatta',
      author_email='bhujay.bhatta@yahoo.com',
      license='Apache Software License',
      packages=find_packages(),
#       package_data={
#         # If any package contains *.txt or *.rst files, include them:
#         '': ['*.txt', '*.rst', '*.yml'],
#         # And include any *.msg files found in the 'hello' package, too:
#         #'hello': ['*.msg'],
#     },
      include_package_data=True,
      install_requires=[
          'requests==2.20.1',
          'configparser==3.5.0',
          'PyJWT==1.7.0',
          'PyYAML==3.13',
          'cryptography==2.3.1',
          'six==1.11.0',
          'Flask==1.0.2',
          'Flask-Testing==0.7.1',
          'Flask-Migrate==2.3.1',
          'Flask-SQLAlchemy==2.3.2',
          'konfig==1.1',
          'tokenleaderclient==0.71',
          'pyOpenSSL==19.0.0',
          
      ],
      entry_points = {
        'console_scripts': ['adminops=tokenleader.app1.adminops.admin_cli_parser:main',
                            'tokenleader-start=tokenleader.app_run:main'],
        },
      test_suite='nose.collector',
      tests_require=['nose'],

      zip_safe=False)
