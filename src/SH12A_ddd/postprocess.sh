pwdir=`pwd`     # save present working directory
wdir=wdir       # working directory tree for base SH12A files, relative to pwdir
ddir=wdir_ddd   # target directory tree for resulting ddd files, relative to pwdir

# create target DDD directory
mkdir -p $ddir

# Switch to target DDD dir and add a file for documentation.
cd $ddir
echo "DDD kernel files calculated on ${HOSTNAME} by ${USER}" > README.md
echo "Date:" `date` >> README.md
echo "" >> README.md
echo "Description">> README.md
echo "-----------">> README.md
echo "(add your description here)" >> README.md
echo "" >> README.md

#switch to wdir and build all
cd $pwdir/$wdir
for shdir in $(find . -mindepth 3 -maxdepth 3 -type d )
do
    echo
    echo "Processing directory: "$wdir/$shdir

	cd $shdir
	echo convertmc tripddd --many "*.bdo"
    cd $pwdir

    # strip energy directory from dir current dir name
    tdir=`dirname $shdir`

    # build energy specific target directory and copy ddd file to it
    targetdir=$ddir/$tdir
    mkdir -p $targetdir
    echo cp -v $shdir/*.ddd $targetdir/.
done
