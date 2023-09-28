"""

******************************************************************************
Cours     :     Dispositifs à Semiconducteurs
TP        :     TP3
Intitulé  :     Démodulation AM
******************************************************************************

@author: marco.mazza (marco.mazza@hefr.ch)
@author: armando.bourgknecht (armando.bourgknecht@hefr.ch)
"""
# %% Imports

import pyvisa as visa # interface pour instrumentation
import time # ajout de délai entre les instructions

# %% Paramètres de connexion

mso_address = "USB0::10893::6000::MY55440268::INSTR"

# %% Connexion et initialisation

rm = visa.ResourceManager()             # Object de gestion des équipements
mso = rm.open_resource(mso_address)     # Connexion à l'appareil

mso.write("*IDN?")      # Demande l'identificatif de l'appareil
print(mso.read())       # Affichage de la reponse

mso.write("*CLS")       # Initialisation
mso.write("*RST")       # Remise à zéro de la configuration

time.sleep(2)           # attente de 2 secondes

# %% Configuration de l'échelle de temps (commande :TIM)

mso.write(":TIM:RANG 0.002")# TODO: régler l'échelle de temps pour afficher deux périodes

# %% Configuration des canaux (commande :CHAN)

mso.write(":CHAN1:DISP ON")# TODO: Canal1 - afficher le canal
mso.write(":CHAN1:OFFS 0")# TODO: Canal1 - régler la composante continue à 0V
mso.write(":CHAN1:SCAL 0.5")# TODO: Canal1 - échelle d'amplitude à 0.5 V/div
mso.write(":CHAN1:IMP ONEM")# TODO: Canal1 - haute impédance de sortie (1Meg Ohm)

mso.write(":CHAN2:DISP ON")# TODO: Canal2 - afficher le canal
mso.write(":CHAN2:OFFS 0")# TODO: Canal2 - régler la composante continue à 0V
mso.write(":CHAN2:SCAL 0.5")# TODO: Canal2 - échelle d'amplitude à 0.5 V/div
mso.write(":CHAN2:IMP ONEM")# TODO: Canal2 - haute impédance de sortie (1Meg Ohm)

mso.write(":CHAN3:DISP OFF")# TODO: Canal3 - cacher le canal
mso.write(":CHAN4:DISP OFF")# TODO: Canal4 - cacher le canal

# %% Configuration du signal (commande :WGEN)

mso.write(":WGEN:FUNCtion SIN")# TODO: Signal de porteuse - Génération du signal sinusoïdal
mso.write(":WGEN:FREQ 200000")# TODO: Signal de porteuse - Réglage de la fréquence
mso.write(":WGEN:VOLTage 5")# TODO: Signal de porteuse - Amplitude de 5V

mso.write(":WGEN:MOD:FUNC SQU")# TODO: Modulation - Génération du signal carré
mso.write(":WGEN:MOD:AM:FREQ 1000")# TODO: Modulation - Modulation AM à 1kHz
mso.write(":WGEN:MOD:AM:DEPT 50")# TODO: Modulation - Profondeur de modulation à 50%
mso.write(":WGEN:MOD:STAT 1")# TODO: Modulation - Activation de la modulation AM

mso.write(":WGEN:OUTPut:LOAD ONEMeg")
mso.write(":WGEN:OUTPut ON")

# %% Configuration du trigger (commande :TRIG)

mso.write(":TRIGger:SOURce CHANnel1")
mso.write(":TRIGger:LEVel 1")

time.sleep(2)
mso.write(":STOP")

# %% Acquisition des métadonnées
mso.write(":WAVeform:FORMat ASCii")
mso.write(":WAVeform:PREamble?")

preamble = mso.read().split(',')

time.sleep(1)

step = float(preamble[4])
cnt = int(preamble[2])

# %% Acquisition des données

# Canal 1
mso.write(":WAVeform:SOURce CHANnel1")
mso.write(":WAVeform:DATA?")

data_ch1 = mso.read().split(',')

ff = open('CH1.txt','w')

for x in range(1,cnt):
    to_write = f"{x*step} \t {data_ch1[x]}\n"
    ff.write(to_write)
    #ff.write(str(x*step)+'\t'+data[x]+'\n')
ff.close()

# Canal 2
mso.write(":WAVeform:SOURce CHANnel2")
mso.write(":WAVeform:DATA?")

time.sleep(1)

data_ch2 = mso.read().split(',')
ff=open('CH2.txt','w')

for x in range(1,cnt):
    to_write = f"{x*step} \t {data_ch2[x]}\n"
    ff.write(to_write)
    #ff.write(str(x*step)+'\t'+data_ch2[x]+'\n')
ff.close()

# %% Fermeture de la connexion

mso.close()
