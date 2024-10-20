from setuptools import find_packages, setup

setup(
    name='fixture',
    version='1.0.0',
    description='Allows to inject class-based fixtures to any test classes.',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    author='Adam Lewandowski',
    author_email='adam_lewandowski_1998@outlook.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 5.1',
        'Framework :: Pytest',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities'
    ]
)
