"""

******************************************************************************
Cours     :     Dispositifs à Semiconducteurs
TP        :     TP1-C
Intitulé  :     Caractérisation de la capacité d'inversion d'une diode
******************************************************************************

@author: marco.mazza (marco.mazza@hefr.ch)
@author: armando.bourgknecht (armando.bourgknecht@hefr.ch)
"""

# %% Imports

import pyvisa as visa # interface pour instrumentation
import time # ajout de délai entre les instructions

import matplotlib.pyplot as plt # outil pour tracer des graphes
import numpy as np # bibliothèque de mathématiques numériques

# %% Paramètres

mso_address = "USB0::10893::6000::MY55440269::INSTR" # adresse oscilloscope

fstart = 380     # fréquence de start, Hz
fstop = 38000      # fréquence de stop, Hz
ferr = 0.1     # écart de tolérance de fréquence, Hz

R = 97850       # valeur de la résistance ( !! Mesurer à l'impédance-mètre !! )

# Valeurs extraites de la fiche technique de la diode varicap BB112
# Ces valeurs seront utiles pour comparer les graphes C_var(V_pol) donnés par
# les mesures expérimentales et la fiche technique.
Vpol_BB112 = [0.5, 1, 2, 3] # Tension de polarisation inverse, V
Cvar_BB112 = [580, 470, 310, 200] # Capacité varicap, pF

# %% Connexion et initialisation

rm = visa.ResourceManager()             # Object de gestion des équipements
mso = rm.open_resource(mso_address)     # Connexion à l'appareil

mso.write("*IDN?")      # Demande l'identificatif de l'appareil
print(mso.read())       # Affichage de la reponse

mso.write("*CLS")       # Initialisation
mso.write("*RST")       # Remise à zéro de la configuration

time.sleep(2)           # attente de 2 secondes

# %% Configuration des canaux (commande :CHAN)

mso.write(":CHAN1:DISP ON")
mso.write(":CHAN1:OFFS 0")
mso.write(":CHAN1:SCAL 0.05")
mso.write(":CHAN1:COUP AC")
 
mso.write(":CHAN2:DISP ON")
mso.write(":CHAN2:OFFS 0")
mso.write(":CHAN2:SCAL 0.05")
mso.write(":CHAN2:COUP AC") 

mso.write(":CHAN3:DISP OFF")
mso.write(":CHAN4:DISP OFF")

# %% Configuration du trigger (commande :TRIG)

mso.write(":TRIG:SOUR CHAN1")
mso.write(":TRIG:LEV 0")
mso.write(":TRIG:EDGE:SLOP POS")

# %% Configuration du signal (commande :WGEN)

mso.write(":WGEN:FUNC SIN")
mso.write(":WGEN:VOLT 0.3")             # amplitude peak2peak
mso.write(":WGEN:VOLT:OFFS 0")          # offset
mso.write(":WGEN:OUTPut ON")

# %% Configuration des paramètres d'acquisition (commandes :ACQ et :MEAS)

mso.write(":MEAS:CLE")

mso.write(":ACQ:TYPE AVER")
mso.write(":ACQ:COUN 8")

# %% Mesures (commandes :WGEN, :TIM et :MEAS)

Vpol_meas = [0, 0.5, 1, 1.5, 2, 2.5]     # tableau de tensions de polarisation
Cvar_meas = np.zeros(len(Vpol_meas))     # tableau pour stocker les mesures de capacité

j = 0   # indice pour stocker la capacité dans le tableau à la position 'j'

# Itération pour chaque tension de polarisation
for Vpol in Vpol_meas:

    i = 0   # indice pour compter le nombre d'étapes pour trouver la fréquence de coupure

    f1 = fstart  # Recherche dichotomique : début du tableau en f1
    f2 = fstop   # Recherche dichotomique : fin du tableau en f2

    mso.write(f":WGEN:VOLT:OFFS {Vpol}")    # applique la tension de polarisation

    # Boucle pour trouver la fréquence de coupure    
    while( ferr < (f2 - f1) ):
        
        i = i + 1   # Incrémente le compte du nombre d'étapes pour trouver la fréquence de coupure
        
        ff = np.sqrt(f1 * f2)   # Calcule la fréquence moyenne à appliquer par moyenne logarithmique
        
        period = 1/ff   # Change la fréquence du signal
        mso.write(f":WGEN:PER {period}")    # TODO : définir la période du signal
        mso.write(f":TIMebase:RANGe {period*2}" )   # TODO : définir la largeur de la fenêtre d'affichage (2 fois la période)
        time.sleep(1)   # attente de 1 seconde au moins
        
        mso.write(":MEASure:FREQuency? CHANnel1") # mesure de la fréquence sur le canal 1
        freq = float(mso.read())    # stockage de la fréquence dans une variable
        
        mso.write(":MEAS:VAMPlitude? CHAN1")    # TODO : mesure de l'amplitude du signal sur le canal 1 (signal d'entrée)
        amp1 = float(mso.read())     # TODO : stockage de l'amplitude d'entrée dans une variable
        
        mso.write(":MEAS:VAMPlitude? CHAN2")    # TODO : mesure de l'amplitude du signal sur le canal 2 (signal de sortie)
        amp2 = float(mso.read())    # TODO : stockage de l'amplitude de sortie dans une variable
        
        amplitude_dB = 20*np.log10(amp2/amp1)     # TODO : calcul du gain en dB et stockage dans une variable
        
        # Recherche dichotomique
        if (amplitude_dB < -3.01):
            # la valeur est dans la partie gauche du tableau
            f2 = ff
        else:
            # la valeur est dans la partie droite du tableau
            f1 = ff

    Cvar_meas[j] = 1E12/(2*np.pi*R*freq)    # stockage de la valeur de la capacité varicap
    
    j = j + 1   # Incrémente pour stocker la prochaine valeur de capacité dans le tableau
    
    print(f"Vpol = {Vpol:.1f}V \t Step: {i} \t G = {amplitude_dB:.6f}dB \t @f = {ff:.2f}Hz \t C = {Cvar_meas[j-1]:.3f}")

# %% Fermeture de la connexion

mso.close()

# %% Affichage des résultats

# Affiche sur un même graphe Cvar(Vpol) avec :
#   - Les valeurs mesurées (bleu)
#   - Les valeurs de la fiche technique (rouge)
plt.plot(Vpol_meas, Cvar_meas, 'b^-', label="Measurement")
plt.plot(Vpol_BB112, Cvar_BB112, 'r^:', label="Datasheet")
plt.xlabel('Tension de polarisation $V_{pol}$, V')
plt.ylabel('Capacité varicap $C_{var}$, pF')
plt.legend(loc="upper right")
plt.show()
