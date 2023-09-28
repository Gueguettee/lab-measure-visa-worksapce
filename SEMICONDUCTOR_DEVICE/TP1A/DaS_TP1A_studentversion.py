"""

******************************************************************************
Cours     :     Dispositifs à Semiconducteurs
TP        :     TP1-A
Intitulé  :     Caractérisation de la capacité d'inversion d'une diode
******************************************************************************

@author: marco.mazza (marco.mazza@hefr.ch)
@author: armando.bourgknecht (armando.bourgknecht@hefr.ch)
"""

# %% Imports

import pyvisa as visa # interface pour instrumentation
import time

# %% Paramètres

# Connecter le câble USB
# Trouver l'adresse USB du MSOX3034T
# Bouton "Utility" > onglet "E-S" / "I/O"
mso_address = "USB0::10893::6000::MY55440269::INSTR"

# %% Connexion et initialisation

rm = visa.ResourceManager()         # Object de gestion des équipements
mso=rm.open_resource(mso_address)   # Connexion à l'appareil

mso.write("*IDN?")      # Demande l'identificatif de l'appareil
print(mso.read())       # Affichage de la reponse

mso.write("*CLS")       # Initialisation
mso.write("*RST")       # Remise à zéro de la configuration

# %% Configuration de la largeur de la fenêtre temporelle

mso.write(":TIMebase:RANGe 1E-3" )      # Réglage de la largeur de la fenêtre

# %% Configuration des canaux (commande :CHANnel)

# Connecter un câble coaxial (RG-58) entre "GEN OUT" et "CHANNEL 1"

mso.write(":CHANnel1:DISPlay ON" )      # Afficher le canal 1
mso.write(":CHANnel2:DISPlay OFF")      # Cacher le canal 2
mso.write(":CHANnel3:DISPlay OFF")      # Cacher le canal 3
mso.write(":CHANnel4:DISPlay OFF")      # Cacher le canal 4

mso.write(":CHANnel1:SCALe 1")          # Régler l'échelle du canal 1 à 1 V/div
mso.write(":CHANnel1:OFFSet 0")         # Régler la composante continue à 0V

# %% Configuration du signal (commande :WGEN)

mso.write(":WGEN:FUNCtion SQUare")              # Définir la forme d'onde (carrée)
mso.write(":WGEN:FREQuency 10E+3")              # Définir la fréquence (10 kHz)
mso.write(":WGEN:FUNCtion:SQUare:DCYCLe 20")    # Définir le rapport cyclique (20%)
mso.write(":WGEN:VOLTage:HIGH 2")               # Définir le niveau haut (2 volt)
mso.write(":WGEN:VOLTage:LOW 0")                # Définir le niveau bas (0 volt)
mso.write(":WGEN:OUTPut ON")                    # Activer la sortie

# %% Configuration du trigger (commande :TRIGger)

mso.write(":TRIGger:SOURce CHANnel1")   # Définir la source du trigger (canal 1)
mso.write(":TRIGger:LEVel 1")           # Définir le niveau du trigger (1 volt)

# %% Configuration de la mesure (commande :MEAS)

time.sleep(1)

#mso.write(":MEAS:FREQ CHAN1")    # Règle la mesure de la fréquence du canal 1
mso.write(":MEAS:FREQ? CHAN1")   # Envoi d'une requête de mesure à l'appareil

print(mso.read())       # Afficher la mesure sur la console Python

#mso.write(":MEASure:VAMPlitude CHANnel1")
mso.write(":MEASure:VAMPlitude? CHANnel1")     # Envoi d'une requête de mesure à l'appareil

print(mso.read())

# %% Fermeture de la connexion

mso.close()
