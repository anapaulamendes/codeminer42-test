#!/bin/sh
rm -Rf _public
find . -name __pycache__ | xargs rm -Rf
