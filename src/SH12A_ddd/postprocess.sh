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

#switch to wdir and convert all bdo files to ddd files
cd $pwdir/$wdir
for shdir in $(find . -mindepth 3 -maxdepth 3 -type d )
do
    echo
    echo "Processing directory: "$wdir/$shdir

	  cd $shdir
	  convertmc tripddd --many "*.bdo"
    cd $pwdir
done

cd $pwdir
find $wdir -name "*.ddd"  | xargs -i sh -c 'echo {}; echo {} | mkdir -p $ddir/`cut -d/ -f3-4`/; cp -v {} $ddir/`cut -d/ -f3-4`/'