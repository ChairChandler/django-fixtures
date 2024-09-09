from setuptools import setup

setup(
    name='fixtures',
    version='1.0.0',
    description='Allows to inject class-based fixtures to any test classes.',
    package_dir={'fixture': 'src'},
    author='Adam Lewandowski',
    author_email='adam_lewandowski_1998@outlook.com',
    classifiers=[
        'Private :: Do Not Upload',
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 5.1',
        'Framework :: Pytest',
        'Programming Language :: Python :: 3.11',
        'License :: Free for non-commercial use',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities'
    ]
)
