#!/bin/fish
rm ../../python-packages/shop -rfd
mkdir ../../python-packages/shop
cp . ../../python-packages/shop -r
cd ../../python-packages/shop
echo "Publishing to PyPI!"
flit publish
echo "Pushing to Github!"
git add --all
git commit
git push
