Introduction
------------
This script collection calculates depth dose beam kernel data for the treatment planning system TRiP98 using the Monte Carlo particle transport code [SHIELD-HIT12A](https://shieldhit.org).

Usage
-----

Switch to the directory: `TRiPbase/src/SJ12A_ddd`.

1) modify `config.dat` file with files and energy ranges, etc.
You can also adjust the beam model by adjusting parameters in `beam.dat` and for more complex
beam models (e.g. when divergence and focus changes as a function of energy) this can easily be coded in `prepare.py`.


2) Autogenerate directories:
```
$ python3 prepare.py
```
which will create a new wdir/ directory holding all the individual energy and projectile MC setups.


3) Submit to cluster to calculate these
```
$ ./submit.sh
```
which will populate the wdir/. subdirectories with .bdo files.

4) Process results
```
$ ./postprocess.sh
```
which search and covert the .bdo files and copy the resulting .ddd files to a new ./ddd directory.
