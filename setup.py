from setuptools import setup, find_packages

setup(
    name='compipe',         # How you named your package folder (MyLib)
    version='0.2.7',      # Start with a small number and increase it with every change you make
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    license='MIT',
    # Give a short description about your library
    description='a lite version of the command wrapper for python',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='esunvoteb',                   # Type in your name
    author_email='esun@voteb.com',      # Type in your E-Mail
    # Provide either the link to your github or to your website
    url='https://github.com/ImagineersHub/compipe',
    # download_url='https://github.com/ImagineersHub/compipe/archive/v_01.tar.gz',    # I explain this later on
    # Keywords that define your package best
    keywords=['python', 'command', 'commandlet', 'cmd', 'cmdlet'],
    packages=find_packages(exclude=["unitest", "compipe_logs"]),
    install_requires=[            # I get to this in a second
        'requests>=2.28.2',
        'cryptography>=36',
        'tqdm>=4.63.0',
        'wrapt>=1.13',
        'google-api-python-client>=2.39',
        'colorlog'
    ],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 3 - Alpha',
        # Define that your audience are developers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': [
            'unittest = compipe.unittest.cmd_test:main',
        ],
    }
)
