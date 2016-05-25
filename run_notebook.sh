#!/bin/bash

# #

d=`/bin/pwd`
PYTHONPATH=$d:$d/../ca-steel-design/lib:$PYTHONPATH jupyter notebook $*
