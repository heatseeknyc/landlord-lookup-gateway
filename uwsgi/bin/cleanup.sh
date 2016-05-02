#!/bin/sh -ue
find pylib -name '__pycache__' | xargs \rm -rf 
find logs -name '*.log' | xargs \rm -rf 
