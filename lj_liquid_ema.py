
#
# Copyright (C) 2013-2019 The ESPResSo project
#
# This file is part of ESPResSo.
#
# ESPResSo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ESPResSo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Simulate a Lennard-Jones fluid maintained at a fixed temperature
by a Langevin thermostat. Shows the basic features of how to:

* set up system parameters, particles and interactions.
* warm up and integrate.
* write parameters, configurations and observables to files.

The particles in the system are of two types: type 0 and type 1.
Type 0 particles interact with each other via a repulsive WCA
interaction. Type 1 particles neither interact with themselves
nor with type 0 particles.
"""
import sys

import numpy as np
import espressomd
import datetime

required_features = ["LENNARD_JONES"]
espressomd.assert_features(required_features)

name = "lj_liquid"
param = [10.7433, 0.7, 1]

if len(sys.argv == 3):
    default = []
    for i in range(1, 4):
        if sys.argv[i] != "-":
            default.append(sys.argv[i])
        else:
            default.append(param[i])
    param = default
# Files
#############################################################
logfile = open(f"{name}.log", 'w')
xyzfile = open(f"{name}.xyz", 'w')
obsfile = open(f"{name}.obs", 'w')

#############################################################
logfile.write(f"""
=======================================================
=                    {name}.py                     =
=======================================================\n
""")


# System parameters
#############################################################

box_l = param[0]
density = param[1]

# Interaction parameters (repulsive Lennard-Jones)
#############################################################

lj_eps = 1.0
lj_sig = 1.0
lj_cut = 2.5 * lj_sig

# Integration parameters
#############################################################
system = espressomd.System(box_l=[box_l] * 3)
np.random.seed(seed=42)

system.time_step = 0.01
system.cell_system.skin = 0.4

# warmup integration (steepest descent)
warm_steps = 20
warm_n_times = 10
# convergence criterion (particles are separated by at least 90% sigma)
min_dist = 0.9 * lj_sig

# integration
int_steps = 1000
int_n_times = 10


#############################################################
#  Setup System                                             #
#############################################################

# Interaction setup
#############################################################
system.non_bonded_inter[0, 0].lennard_jones.set_params(
    epsilon=lj_eps, sigma=lj_sig, cutoff=lj_cut, shift="auto")

logfile.write("LJ-parameters:\n")
logfile.write(f"{system.non_bonded_inter[0, 0].lennard_jones.get_params()}\n")

# Particle setup
#############################################################

volume = box_l**3
n_part = int(volume * density)

for i in range(n_part):
    system.part.add(pos=np.random.random(3) * system.box_l)

logfile.write(
    f"Simulate {n_part} particles in a cubic box of length {box_l} at density {density}.\n")
logfile.write("Interactions:\n")
act_min_dist = system.analysis.min_dist()
logfile.write(f"Start with minimal distance {act_min_dist}\n")


#############################################################
#  Warmup Integration                                       #
#############################################################

logfile.write(f"""\
Start warmup integration:
At maximum {warm_n_times} times {warm_steps} steps
Stop if minimal distance is larger than {min_dist}\n""")
logfile.write(f"{system.non_bonded_inter[0, 0].lennard_jones}\n")

# minimize energy using min_dist as the convergence criterion
system.integrator.set_steepest_descent(f_max=0, gamma=1e-3,
                                       max_displacement=lj_sig / 100)
i = 0
while i < warm_n_times and system.analysis.min_dist() < min_dist:
    logfile.write(f"minimization: {system.analysis.energy()['total']:+.2e}\n")
    system.integrator.run(warm_steps)
    i += 1

logfile.write(f"minimization: {system.analysis.energy()['total']:+.2e}")
logfile.write(f'\n')
system.integrator.set_vv()

# activate thermostat
system.thermostat.set_langevin(kT=1.0, gamma=1.0, seed=42)

# Just to see what else we may get from the C++ core
#import pprint
#pprint.pprint(system.cell_system.get_state(), width=1)
# pprint.pprint(system.part.__getstate__(), width=1)
#pprint.pprint(system.__getstate__())


#############################################################
#      Integration                                          #
#############################################################
logfile.write(f"\nStart integration: run {int_n_times} times {int_steps} steps\n")

for i in range(int_n_times):
    logfile.write(f"run {i} at time={system.time:.2f}")

    system.integrator.run(steps=int_steps)

    energy = system.analysis.energy()
    pressure = system.analysis.pressure()
    obsfile.write(f'{i},{energy["kinetic"]},{energy["bonded"]+energy["non_bonded"]}, {energy["total"]},{pressure["total"]}')
    obsfile.write(f"\n")
    xyzfile.write(f'{n_part}\n')
    xyzfile.write(f"%\n")
    for p in system.part:
        xyzfile.write(f"part {p.pos[0]} {p.pos[1]} {p.pos[2]}")
        xyzfile.write(f"\n")



# terminate program
logfile.write("\nFinished.")
