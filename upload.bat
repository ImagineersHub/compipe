@echo off
cd path\to\your\package

REM Delete the contents of the dist folder
if exist dist rmdir /s /q dist

python setup.py sdist bdist_wheel
twine upload --verbose -u __token__ -p %PYPI_API_TOKEN% dist\*