import os
import sys
import logging
import numpy as np

logger = logging.getLogger(__name__)


class Ion(object):
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
    def __init__(self):
        self.beam = []
        self.geo = []
        self.mat = []
        self.det = []

    def read(self, dir):
        fname_beam = os.path.join(dir, "beam.dat")
        fname_geo = os.path.join(dir, "geo.dat")
        fname_mat = os.path.join(dir, "mat.dat")
        fname_det = os.path.join(dir, "detect.dat")

        with open(fname_beam) as file:
            self.beam = file.readlines()
        with open(fname_geo) as file:
            self.geo = file.readlines()
        with open(fname_mat) as file:
            self.mat = file.readlines()
        with open(fname_det) as file:
            self.det = file.readlines()

    def write(self, ion):
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

    def generate_dats(self, ion, energy, nstat, nsave, rifi=False):
        print(energy)
        if rifi:
            r = 2
        else:
            r = 0
        self.path = os.path.join(".", "wdir", ion.name, "{:05.2f}".format(energy))
        self.beam = [line.replace('$JPART', "{:6d}".format(ion.jpart)) for line in self.beam]
        self.beam = [line.replace('$ENERGY', "{:6.2f}".format(energy)) for line in self.beam]
        self.beam = [line.replace('$SIGX', "{:5.2f}".format(ion.fwhm / 2.355)) for line in self.beam]
        self.beam = [line.replace('$SIGY', "{:5.2f}".format(ion.fwhm / 2.355)) for line in self.beam]
        self.beam = [line.replace('$NSTAT', "{:6d}".format(nstat)) for line in self.beam]
        self.beam = [line.replace('$NSAVE', "{:6d}".format(nsave)) for line in self.beam]
        self.geo = [line.replace('$RIF', "{:3d}".format(r)) for line in self.beam]


def read_ions(fname):
    temp_str = np.loadtxt(fname, dtype=str, usecols=0)
    temp_int = np.loadtxt(fname, dtype=int, usecols=(1, 2, 3))
    temp_float = np.loadtxt(fname, dtype=float, usecols=(4, 5, 6, 7, 8))

    ions = [None] * len(temp_str)

    for i, name in enumerate(temp_str):
        print(i)
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
    nstat = 10000
    nsave = 5000
    ions = read_ions("config.dat")
    t = Template()
    t.read("template")
    for ion in ions:
        for energy in np.arange(ion.emin, ion.emax, ion.estep):
            t.generate_dats(ion, energy, nstat, nsave)
            t.write(ion)


if __name__ == '__main__':
    logging.basicConfig()
    sys.exit(main(sys.argv[1:]))
