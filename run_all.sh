#!/bin/bash
set -e

echo "=========================================================="
echo "    Starting MUGEN FULLSIZE + GZIP Extraction"
echo "=========================================================="
python3 tools/mugen_extractor/mugen_extractor.py --mode FULLSIZE --compress

echo "=========================================================="
echo "    Extraction Complete. Starting RPi Image Build (14G)"
echo "=========================================================="
bash wait_and_build.sh

echo "=========================================================="
echo "    ALL DONE!"
echo "=========================================================="
