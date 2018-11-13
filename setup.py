from setuptools import setup, find_packages


# Extract version info from library
version_info = {}
with open('adnotatio_server/_version.py') as version_file:
    exec(version_file.read(), version_info)


setup(
    name='adnotatio_server',
    description="An example server implementation in Python for the Adnotatio annotation project.",
    version=version_info['__version__'],
    author=version_info['__author__'],
    author_email=version_info['__author_email__'],
    packages=find_packages(),
    install_requires=version_info['__dependencies__'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
