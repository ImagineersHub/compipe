from setuptools import setup, find_packages

setup(
    name='compipe',         # How you named your package folder (MyLib)
    version='0.1.32',      # Start with a small number and increase it with every change you make
    license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='a lite version of the command wrapper for python',   # Give a short description about your library
    author='esunvoteb',                   # Type in your name
    author_email='esun@voteb.com',      # Type in your E-Mail
    url='https://github.com/ImagineersHub/compipe',   # Provide either the link to your github or to your website
    # download_url='https://github.com/ImagineersHub/compipe/archive/v_01.tar.gz',    # I explain this later on
    keywords=['python', 'command', 'commandlet', 'cmd', 'cmdlet'],   # Keywords that define your package best
    packages=find_packages(),
    install_requires=[            # I get to this in a second
        'requests>=2.27.*',
        'cryptography>=36.*',
        'tqdm>=4.63.0',
        'wrapt>=1.13.*',
        'google-api-python-client>=2.39.*'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        'Programming Language :: Python :: 3.7',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
