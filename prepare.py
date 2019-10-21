import os
import sys
import logging
import numpy as np

logger = logging.getLogger(__name__)


class Ion(object):
    """
    Class holding all attributes for a single ion configuration.
    """

    def __init__(self):
        self.name = ""
        self.jpart = 0
        self.z = 0
        self.n = 0
        self.u = 0.0
        self.emin = 0.0
        self.emax = 0.0
        self.estep = 0.0
        self.fwhm = 0.0


class Template(object):
    """
    Class for manipulating the SHIELD-HIT12A input files.
    """

    def __init__(self):
        # placeholder for SH12A templates
        self.tbeam = []
        self.tgeo = []
        self.tmat = []
        self.tdet = []

        # placeholder for output
        self.beam = []
        self.geo = []
        self.mat = []
        self.det = []

        self.rifi_path = ""  # relative path from current wdir to rifi path.
        self.template_dir = ""

    def read(self, dir):
        """
        Reads the template files, and stores them in self object.
        """
        fname_beam = os.path.join(dir, "beam.dat")
        fname_geo = os.path.join(dir, "geo.dat")
        fname_mat = os.path.join(dir, "mat.dat")
        fname_det = os.path.join(dir, "detect.dat")

        self.template_dir = dir

        with open(fname_beam) as file:
            self.tbeam = file.readlines()
        with open(fname_geo) as file:
            self.tgeo = file.readlines()
        with open(fname_mat) as file:
            self.tmat = file.readlines()
        with open(fname_det) as file:
            self.tdet = file.readlines()

    def write(self, ion):
        """
        Write the SH12A output files to self.path for given ion.
        Stopping power files are symlinked to the files found in template/
        """
        try:
            os.makedirs(self.path)
        except FileExistsError:
            pass

        fname_beam = os.path.join(self.path, "beam.dat")
        fname_geo = os.path.join(self.path, "geo.dat")
        fname_mat = os.path.join(self.path, "mat.dat")
        fname_det = os.path.join(self.path, "detect.dat")

        with open(fname_beam, 'w') as file:
            file.writelines(self.beam)
        with open(fname_geo, 'w') as file:
            file.writelines(self.geo)
        with open(fname_mat, 'w') as file:
            file.writelines(self.mat)
        with open(fname_det, 'w') as file:
            file.writelines(self.det)

        # create symlinks to external stopping power files.
        dedx_list = ["Water.txt", "Lucite.txt"]
        for fn in dedx_list:
            try:
                os.symlink(os.path.join("../../../..", self.template_dir, fn), os.path.join(self.path, fn))
            except FileExistsError:
                pass

    def generate_dats(self, ion, energy, nstat, nsave, rifi=False):
        """
        Generate the input files for SH12A, and store these to self.
        """
        if rifi:
            r = 3  # ripple filter material ID, change according to mat.dat
            _rifidir = "RF3MM"
        else:
            r = 0
            _rifidir = "RF0MM"

        # TODO: rename "path" -> "dir"
        self.path = os.path.join(".", "wdir", ion.name, _rifidir, "{:06.2f}".format(energy))

        # first line should read from template.
        self.beam = [line.replace('$JPART', "{:6d}".format(ion.jpart)) for line in self.tbeam]
        if ion.jpart == 25:  # Heavy ions
            self.beam.append("HIPROJ     	{:2d}    {:2d}\n".format(ion.n, ion.z))  # OK to add at the bottom

        self.beam = [line.replace('$ENERGY', "{:7.2f}".format(energy)) for line in self.beam]
        self.beam = [line.replace('$SIGX', "{:5.2f}".format(ion.fwhm / 2.355)) for line in self.beam]
        self.beam = [line.replace('$SIGY', "{:5.2f}".format(ion.fwhm / 2.355)) for line in self.beam]
        self.beam = [line.replace('$NSTAT', "{:6d}".format(nstat)) for line in self.beam]
        self.beam = [line.replace('$NSAVE', "{:6d}".format(nsave)) for line in self.beam]

        if rifi:
            self.beam.append("BMODMC          1                ! For MC ripple filter\n")
            # specifying zone 4, and filename of ripple filter
            self.beam.append("USEBMOD         4 {}\n".format(self.rifi_path))

        self.geo = [line.replace('$RIF', "{:4d}".format(r)) for line in self.tgeo]

        self.mat = self.tmat
        self.det = self.tdet


def read_config(fname):
    """
    Read the config file, returns list of Ion objects.
    """
    temp_str = np.loadtxt(fname, dtype=str, usecols=0)
    temp_int = np.loadtxt(fname, dtype=int, usecols=(1, 2, 3))
    temp_float = np.loadtxt(fname, dtype=float, usecols=(4, 5, 6, 7, 8))

    ions = [None] * len(temp_str)

    for i, name in enumerate(temp_str):
        ions[i] = Ion()
        ions[i].name = name
        ions[i].jpart = temp_int[i][0]
        ions[i].z = temp_int[i][1]
        ions[i].n = temp_int[i][2]
        ions[i].u = temp_float[i][0]
        ions[i].emin = temp_float[i][1]
        ions[i].emax = temp_float[i][2]
        ions[i].estep = temp_float[i][3]
        ions[i].fwhm = temp_float[i][4]
    return ions


def main(args):
    """
    Main function.
    """
    logger.setLevel('INFO')
    nstat = 10000
    nsave = 5000

    ions = read_config("config.dat")

    t = Template()
    t.read("template")
    t.rifi_path = "../../../../template/1drifi3.dat"  # relative path to SH12A wdir

    for ion in ions:
        logger.info(ion.name)
        for energy in np.arange(ion.emin, ion.emax, ion.estep):
            t.generate_dats(ion, energy, nstat, nsave, rifi=True)
            t.write(ion)
            t.generate_dats(ion, energy, nstat, nsave, rifi=False)
            t.write(ion)


if __name__ == '__main__':
    logging.basicConfig()
    sys.exit(main(sys.argv[1:]))
