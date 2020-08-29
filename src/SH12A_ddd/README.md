Introduction
------------
This script collection calculates depth dose beam kernel data for the treatment planning system TRiP98 using the Monte Carlo particle transport code [SHIELD-HIT12A](https://shieldhit.org).

Usage
-----

Working directory: `TRiPbase/src/SJ12A_ddd`.

1) modify `config.dat` file with files and energy ranges, etc.

2) Autogenerate directories:
```
$ python3 prepare.py
```

3) Submit to cluster to calculate them
```
$ ./submit.sh
```

4) Process results
```
$ ./postprocess.sh
```

5) You can collect all the resulting .ddd files into an archive using tar:
```
find . -name "*.ddd" | tar -cvf my_archive.tar -T -
```
