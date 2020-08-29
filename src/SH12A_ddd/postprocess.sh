wdir=`pwd`  # present working directory
ddir=../../../data/ddd  # target directory for resulting data, relative to wdir/.

mkdir -p $ddir

cd ${wdir}/wdir
for shdir in $(find . -mindepth 3 -maxdepth 3 -type d )
do
    echo
    echo "Processing directory: "$shdir

	cd $shdir

	convertmc tripddd --many "*.bdo"
    cd ${wdir}/wdir

    # strip energy directory from dir current dir name
    tdir=`dirname $shdir`

    # build target directory
    targetdir=$ddir/$tdir
    mkdir -p $targetdir

    #copy ddd file to proper place
    cp -v $shdir/*.ddd $targetdir/.

done
