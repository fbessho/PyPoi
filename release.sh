# Release steps
# 
# Run this to create distribution packages

python setup.py clean
rm -rf ./build ./dist
python setup.py sdist
python setup.py bdist_wheel --universal

echo "\n==== Files in ./dist ===="
ls -l ./dist

echo "\n==== RELEASE STEPS ===="
echo "Upload to test PyPI"
echo "  twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
echo "\nCheck a package page on test.pypi.org"
echo "  https://test.pypi.org/project/pypoi/"
echo "\nTest pip installation with test.pypi.org"
echo "  <create and activate a new env>"
echo "  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pypoi"
echo "\nUpload to PyPI"
echo "  twine upload dist/*"
