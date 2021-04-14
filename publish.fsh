#!/bin/fish
rm ../../python-packages/shop -rfd
mkdir ../../python-packages/shop
cp . ../../python-packages/shop -r
cd ../../python-packages/shop
flit publish
