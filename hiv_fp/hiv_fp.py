"""
Toy example of HIV-FP nanoproject.
"""

import starsim as ss
import sciris as sc
import matplotlib.pyplot as plt

sc.options(dpi=200)

pars = dict(
    birth_rate = 20,
    death_rate = 10,
    diseases = 'hiv',
    networks = ['maternal', 'mf', 'msm']
)

class Condoms(ss.Intervention):
    def __init__(self, eff=0.95, coverage=0.2, year=2015, **kwargs):
        super().__init__(**kwargs)
        self.eff = eff
        self.coverage = coverage
        self.year = year
        self.factor = 1 - self.eff*self.coverage
        self.applied = False

    def step(self):
        sim = self.sim
        if sim.now >= self.year and not self.applied:
            self.applied = True
            sim.demographics.births.pars.birth_rate *= self.factor
            sim.diseases.hiv.pars.beta *= self.factor


base = ss.Sim(pars, label='Baseline')
intv = ss.Sim(pars, interventions=Condoms(), label='Condoms')

msim = ss.parallel(base, intv)
msim.plot()

plt.show()