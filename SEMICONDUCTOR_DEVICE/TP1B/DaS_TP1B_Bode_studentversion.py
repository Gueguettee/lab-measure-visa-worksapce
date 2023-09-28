"""

******************************************************************************
Cours     :     Dispositifs � Semiconducteurs
TP        :     TP1-B
Intitul�  :     Caract�risation de la capacit� d'inversion d'une diode
******************************************************************************

@author: marco.mazza (marco.mazza@hefr.ch)
@author: armando.bourgknecht (armando.bourgknecht@hefr.ch)
"""

# %% Imports

import pyvisa as visa # interface pour instrumentation
import time # ajout de d�lai entre les instructions

import matplotlib.pyplot as plt # outil pour tracer des graphes
import numpy as np # biblioth�que de math�matiques num�riques

# %% Param�tres

mso_address = "USB0::10893::6000::MY55440268::INSTR" # adresse oscilloscope

fstart=100      # fr�quence de start, Hz
fstop=10E3      # fr�quence de stop, Hz
pts=3          # nombre de points

fstep = np.logspace(np.log10(fstart), np.log10(fstop), num=pts, base=10, endpoint=True)

# %% Connexion et initialisation

rm = visa.ResourceManager()         # Object de gestion des �quipements
mso=rm.open_resource(mso_address)   # Connexion � l'appareil

mso.write("*IDN?")      # Demande l'identificatif de l'appareil
print(mso.read())       # Affichage de la reponse

mso.write("*CLS")       # Initialisation
mso.write("*RST")       # Remise � z�ro de la configuration

time.sleep(2)           # attente de 2 secondes

# %% Configuration des canaux (commande :CHANnel)

mso.write(":CHANnel1:DISPlay ON")# TODO: afficher le canal 1 
mso.write(":CHANnel1:SCALe 1")# TODO: R�gler l'�chelle du canal 1 � 1 V/div
mso.write(":CHANnel1:OFFSet 0")# TODO: R�gler la composante continue � 0V

mso.write(":CHANnel2:DISPlay ON")# TODO: afficher le canal 2
mso.write(":CHANnel2:SCALe 1")# TODO: R�gler l'�chelle du canal 2 � 1 V/div
mso.write(":CHANnel2:OFFSet 0")# TODO: # TODO: R�gler la composante continue � 0V


mso.write(":CHANnel3:DISPlay OFF")# TODO: Cacher le canal 3
mso.write(":CHANnel4:DISPlay OFF")# TODO: Cacher le canal 4

# %% Configuration du trigger (commande :TRIGger)

mso.write(":TRIGger:SOURce CHANnel1")# TODO: D�finir la source du trigger (canal 1)
mso.write(":TRIGger:LEVel 1")# TODO: D�finir le niveau du trigger (1V)

# %% Configuration du signal (commande :WGEN)

mso.write(":WGEN: FUNCtion SIN")# TODO: D�finir la forme d'onde (sinuso�dale)
mso.write(":WGEN:VOLTage 6")# TODO: D�finir l'amplitude (6Vpp)
mso.write(":CHANnel1:OFFSet 0")# TODO: D�finir la composante continue (0 volt)
mso.write(":WGEN:OUTPut ON")# TODO: Activer la sortie

# %% Mesures (commandes :WGEN, :MEAS et :TIM)

mso.write(":MEAS:CLE")      # effacer lew mesures pr�c�dentes
freq = np.zeros(pts)        # tableau pour les fr�quences
gain = np.zeros(pts)        # tableau pour les amplitudes
phase = np.zeros(pts)       # tableau pour le dephasage

for x in range(0,pts):
    
    ff=fstep[x]
    period=1/ff
    
    mso.write(f":WGEN:PER {period}") # d�finir la p�riode du signal
    
    mso.write(f":TIMebase:RANGe {period*2}" )# TODO: d�finir la largeur de la fen�tre d'affichage (2 fois la p�riode)
    
    time.sleep(2)    # attente pour permettre � la sortie de se stabiliser

    mso.write(":MEASure:FREQuency? CHANnel1")# TODO:  demander la mesure de la fr�quence du canal 1   
    freq[x]=float(mso.read())           # lecture du r�sultat et stockage
    
    mso.write(":MEAS:VAMPlitude? CHAN1")# TODO: demander la mesure de l'amplitude du canal 1
    avin=float(mso.read())              # lecture du r�sultat et stockage
    
    mso.write(":MEAS:VAMPlitude? CHANnel2")# TODO: demander la mesure de l'amplitude du canal 2
    avout=float(mso.read())             # lecture du r�sultat et stockage
    gain[x]=20*np.log10(avout/avin)      # calcul du gain en dB
    
    mso.write(":MEASure:PHASe? CHANnel1,CHANnel2")# TODO: demander la mesure du dephasage
    phase[x]=float(mso.read())          # lecture du résultat et stockage

mso.close()

# %% Affichage des r�sultats    

# Magnitude du diagramme de Bode
fig, ax1 = plt.subplots()
ax1.semilogx(freq, gain, 'b-')
ax1.set_xlabel('frequency, Hz')
ax1.set_ylabel('gain, dB', color='b')
ax1.tick_params('y', colors='b')

# Phase du diagramme de Bode
ax2 = ax1.twinx()
ax2.semilogx(freq, phase, 'r-')
ax2.set_ylabel('phase, deg', color='r')
ax2.tick_params('y', colors='r')
fig.tight_layout()

plt.show()
