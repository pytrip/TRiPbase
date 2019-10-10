import os
import numpy as np

def create_dirs():
    try:
        os.makedirs("path/to/directory")
    except FileExistsError:
        # directory already exists
        pass


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


def read_ions(fname):
    temp_str = np.loadtxt(fname, dtype=str, usecols=0)
    temp_int = np.loadtxt(fname, dtype=int, usecols=(1, 2, 3))
    temp_float = np.loadtxt(fname, dtype=float, usecols=(4, 5, 6, 7, 8))

    print(temp_str)
    print("length: ", len(temp_str))
    ions = [None] * len(temp_str)
    print(len(ions))

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

    def generate_dats(self, ion, energy, nstat, nsave):
        self.path = os.path.join(".", ion.name, str(energy))
        self.beam = [line.replace('$JPART', "{:d}".format(ion.jpart)) for line in self.beam]
        self.beam = [line.replace('$ENERGY', "{:f}".format(energy)) for line in self.beam]
        self.beam = [line.replace('$SIGX', "{:f}".format(ion.fwhm / 2.355)) for line in self.beam]
        self.beam = [line.replace('$SIGY', "{:f}".format(ion.fwhm / 2.355)) for line in self.beam]
        self.beam = [line.replace('$NSTAT', "{:d}".format(nstat)) for line in self.beam]
        self.beam = [line.replace('$NSAVE', "{:d}".format(nsave)) for line in self.beam]


nstat = 10000
nsave = 5000
ions = read_ions("config.dat")
t = Template()
t.read("template")
for ion in ions:
    energy = 125.0
    t.generate_dats(ion, energy, nstat, nsave)

print(t.beam)
with open("foobar.dat", 'w') as file:
    file.writelines(t.beam)
print(t.path)
