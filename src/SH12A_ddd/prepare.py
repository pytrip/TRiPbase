import os
import sys
import logging
import numpy as np

logger = logging.getLogger(__name__)


# These are constant now, but the idea is that a more realistic beam model can be added, where these vary
# as a function of energy and particle species.
BEAM_DIV = 2.5        # beam divergence in mrad
BEAM_FOCUS = -200.0      # beam focus relative to beam starting position, positive if upstream (defocussed)
ENERGY_SPREAD = 0.01  # relative energy spread 0.01 = 1 %.

# ripple filter material ID, change according to mat.dat, and AIR if no RIFI
MAT_RIFI = 3          # PMMA
MAT_NORIFI = 4        # AIR

# Zone number if RIFI, as specified in geo.dat
ZONE_RIFI = 4

# list of external stopping powers
DEDX_LIST = ("Water.txt", "Lucite.txt", "Air.txt", "Ti.txt")


class Ion(object):
    """
    Class holding all attributes for a single ion configuration.
    """

    def __init__(self):
        self.name = ""
        self.jpart = 0
        self.z = 0
        self.n = 0
        self.emin = 0.0
        self.emax = 0.0
        self.estep = 0.0
        self.fwhm = 0.0
        self.amuratio = 0.0


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

    @staticmethod
    def fwhm_to_sigma(fwhm):
        """
        Converts FWHM to 1 sigma value.
        """
        return fwhm / (2.0 * np.sqrt(2.0 * np.log(2.0)))

    def read(self, dir_path):
        """
        Reads the template files, and stores them in self object.
        """
        fname_beam = os.path.join(dir_path, "beam.dat")
        fname_geo = os.path.join(dir_path, "geo.dat")
        fname_mat = os.path.join(dir_path, "mat.dat")
        fname_det = os.path.join(dir_path, "detect.dat")

        self.template_dir = dir_path

        with open(fname_beam) as file:
            self.tbeam = file.readlines()
        with open(fname_geo) as file:
            self.tgeo = file.readlines()
        with open(fname_mat) as file:
            self.tmat = file.readlines()
        with open(fname_det) as file:
            self.tdet = file.readlines()

    def write(self):
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
        for fn in DEDX_LIST:
            try:
                os.symlink(os.path.join("../../../..", self.template_dir, fn), os.path.join(self.path, fn))
            except FileExistsError:
                pass

    def generate_dats(self, ion, energy, nstat, nsave, rifi=False):
        """
        Generate the input files for SH12A, and store these to self.
        Input energy must be in E/amu, not in E/nucleon.
        """
        if rifi:
            r = MAT_RIFI
            _rifidir = "RF3MM"
        else:
            r = MAT_NORIFI
            _rifidir = "RF0MM"

        # TODO: rename "path" -> "dir"
        self.path = os.path.join(".", "wdir", ion.name, _rifidir, "{:06.2f}".format(energy))

        # first line should read from template.
        self.beam = [line.replace('$JPART', "{:6d}".format(ion.jpart)) for line in self.tbeam]
        if ion.jpart == 25:  # Heavy ions
            self.beam.append("HIPROJ     	{:2d}    {:2d}\n".format(ion.n, ion.z))  # OK to add at the bottom

        _e_nuc = energy * ion.amuratio
        self.beam = [line.replace('$ENERGY', "{:12.5f}".format(_e_nuc)) for line in self.beam]
        self.beam = [line.replace('$D_ENERGY', "{:12.5f}".format(_e_nuc * ENERGY_SPREAD)) for line in self.beam]
        _sigma = self.fwhm_to_sigma(ion.fwhm)
        self.beam = [line.replace('$SIGX', "{:6.3f}".format(_sigma)) for line in self.beam]
        self.beam = [line.replace('$SIGY', "{:6.3f}".format(_sigma)) for line in self.beam]
        self.beam = [line.replace('$NSTAT', "{:6d}".format(nstat)) for line in self.beam]
        self.beam = [line.replace('$NSAVE', "{:6d}".format(nsave)) for line in self.beam]

        self.beam.append("BEAMDIV        {:6.3f} {:6.3f} {:6.3f}  ! beam divergence \n".format(BEAM_DIV,
                                                                                               BEAM_DIV,
                                                                                               BEAM_FOCUS))

        if rifi:
            self.beam.append("BMODMC          1                ! For MC ripple filter\n")
            # specifying zone 4, and filename of ripple filter
            self.beam.append("USEBMOD         {:d} {}\n".format(ZONE_RIFI, self.rifi_path))

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
        ions[i].emin = temp_float[i][0]
        ions[i].emax = temp_float[i][1]
        ions[i].estep = temp_float[i][2]
        ions[i].fwhm = temp_float[i][3]
        ions[i].amuratio = temp_float[i][4]
    return ions


def main(args):
    """
    Main function.
    """
    logger.setLevel('INFO')
    nstat = 200000
    nsave = 50000

    ions = read_config("config.dat")

    t = Template()
    t.read("template")
    t.rifi_path = "../../../../template/1drifi3.dat"  # relative path to SH12A wdir

    for ion in ions:
        logger.info(ion.name)
        for energy in np.arange(ion.emin, ion.emax, ion.estep):
            t.generate_dats(ion, energy, nstat, nsave, rifi=True)
            t.write()
            t.generate_dats(ion, energy, nstat, nsave, rifi=False)
            t.write()


if __name__ == '__main__':
    logging.basicConfig()
    sys.exit(main(sys.argv[1:]))
