#!/bin/sh
#deze file start de pipelijn.
#author: Alex Hoogkamer
cd ..
python bin/Trim/Trim.py echte-data.fa 46 0.05
python bin/BLAST/script1.py
python bin/Quality/Quality-control.py
python bin/Output/Output.py
echo "done"
