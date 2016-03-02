#!/bin/bash

# #

d=`/bin/pwd`
PYTHONPATH=$d:$PYTHONPATH jupyter notebook
