"""

******************************************************************************
Cours     :     Dispositifs à Semiconducteurs
TP        :     TP2
Intitulé  :     Caractérisation d'une diode par interpolation
******************************************************************************

@author: marco.mazza (marco.mazza@hefr.ch)
@author: armando.bourgknecht (armando.bourgknecht@hefr.ch)
"""
# %% Imports

import pyvisa as visa # interface pour instrumentation
import time # ajout de délai entre les instructions

import matplotlib.pyplot as plt # outil pour tracer des graphes
import numpy as np # bibliothèque de mathématiques numériques

import pandas as pd # outil de manipulation de données

# %% Paramètres de connexion

rm = visa.ResourceManager()             # Object de gestion des équipements

# 33500B Keysight Waveform Generator
# "System" button > "I/O config" tab > "USB settings" > "Show USB Id"
wg33500b_address = "USB0::2391::10247::MY52402322::0::INSTR" # adresse générateur de fonctions

m34401_address = "GPIB::22" # adresse multimètre

# %% Variables

Vth = 26e-3 # Tension thermique

Vbias_start = 0.25
Vbias_stop = 0.4
Vbias_step = 20
Vbias_array = np.linspace(Vbias_start, Vbias_stop, Vbias_step)

Ibias_array = np.zeros(len(Vbias_array))

# %% Générateur de fonction: Connexion et initialisation

#   Keysight
wg33500b = rm.open_resource(wg33500b_address)

wg33500b.write("*IDN?")
print(f"Found:  {wg33500b.read()}")

wg33500b.write("*RST")

time.sleep(1)

# %% Multimètre: Connexion et initialisation

# 34401A Hewlett-Packard Multimeter
m34401 = rm.open_resource(m34401_address)

m34401.write("*IDN?")
print(f"Found:  {m34401.read()}")

m34401.write("*RST")
m34401.write("*CLS")
# m34401.write("DISPLAY:TEXT \"DIODE-TEST\"")

time.sleep(1)

# %% Génération du signal

wg33500b.write("FUNC DC")
wg33500b.write("OUTP1:LOAD INF")

# %% Mesures

for i in range(len(Vbias_array)):

    print(f"Step #{i}")

    wg33500b.write(f"VOLTage:OFFSet +{Vbias_array[i]}")    # TODO : Régler la tension de polarisation DC
    wg33500b.write("OUTPut ON")    # TODO : Activer la sortie

    time.sleep(0.5)

    m34401.write("MEAS:CURR:DC?")    # TODO : Mesurer le courant DC

    Ibias_array[i] = np.log(float(m34401.read()))    
    
    wg33500b.write("OUTPut OFF")  # TODO : Désactiver la sortie
    
    time.sleep(5)
    
# %% Fermeture des connexions

wg33500b.close()
m34401.close()

# %% Interpolation

regr = np.polyfit(Vbias_array, Ibias_array, 1)

n = 1/(Vth*regr[0])

Is = np.exp(regr[1])
Is_pA = 1e12 * Is # pA

R = np.corrcoef(Vbias_array, Ibias_array)[0,1]
R_square = 100 * (R**2) # %

print("\n\n\n")
print(f"Is = {Is_pA:.1f} pA \t n = {n:.2f}")

print(f"R-square = {R_square:.3f}")

# %% Graphes des résultats

plt.plot(Vbias_array, Ibias_array, 'r^:')
plt.xlabel('Voltage, V')
plt.ylabel('Log of current, log(pA)')
plt.show()

# %% Exportation en CSV

t = np.linspace(0, 1, 100)
v = np.linspace(Vbias_start, Vbias_stop, 100)

df = (pd.DataFrame([t, v])).T

df.to_csv('TP2_Diode.txt', sep=' ', index=False, header=False)
