wdir=`pwd`  # present working directory

cd ${wdir}/wdir
for shdir in $(find . -mindepth 3 -maxdepth 3 -type d )
do
	cd $shdir
	echo $shdir
	# echo sbatch --array 0-16 rsshield.sh
	echo convertmc tripddd --many "*.bdo" --energy 0  # TODO: find a way to put in energy MeV/amu
	cd ${wdir}/wdir
done
