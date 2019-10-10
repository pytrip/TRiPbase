#!/usr/bin/env bash

wdir=`pwd`  # present working directory

cd ${wdir}/wdir
for shdir in $(find . -mindepth 3 -maxdepth 3 -type d )
do
	cd $shdir
	echo $shdir
	# echo sbatch --array 0-16 rsshield.sh
	echo sbatch ../../../../rsshield.sh
	cd ${wdir}/wdir
done
