#import visa
import pyvisa as visa
import time
import string
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

TIME_SLEEP_TRIG = 0.5
TIME_SLEEP_MEAS = 0.2

rm = visa.ResourceManager()
rmlist=rm.list_resources()
matching = [s for s in rmlist if "USB" in s]
mso=rm.open_resource(matching[0])
mso=rm.open_resource("USB0::10893::6000::MY55440269::INSTR")
print(mso.query("*IDN?"))
mso.write("*RST")

### CHANNELS settings
window_time=1E-6
mso.write(":TIMebase:RANGe "+str(window_time))   # set time (window length)
mso.write(":TIMebase:REFerence LEFT")


mso.write(":CHANnel1:DISPlay ON")
mso.write(":CHANnel2:DISPlay OFF")
mso.write(":CHANnel3:DISPlay OFF")
mso.write(":CHANnel4:DISPlay OFF")

mso.write(":CHANnel1:SCALe 0.1")          # V/div
mso.write(":CHANnel1:OFFSet 0.5")

mso.write(":CHANnel1:IMPedance ONEMeg")

V_P = 1
V_N = 0

### WAVEFORM GENERATOR settings
mso.write(":WGEN:FUNCtion SQUare")
mso.write(":WGEN:FREQuency 5E+4")
mso.write(f":WGEN:VOLTage:HIGH {V_P}")
mso.write(f":WGEN:VOLTage:LOW {V_N}")
mso.write(":WGEN:OUTPut ON")

### TRIGGER setttings
mso.write(":TRIGger:SOURce CHANnel1")
mso.write(":TRIGger:LEVel 0.4")

vLight = 2e8
#
# DELAY MEASUREMENT settings
### measure delay use PWIDth measurement
### define thresholds
### evaluate cable length
mso.write(":MEASure:PWIDth CHANnel1")
mso.write(f":MEASure:DEFine THResholds,ABSolute,{(V_P-V_N)/2},{(V_P-V_N)/2*0.9},{(V_P-V_N)/2*0.75}")
time.sleep(TIME_SLEEP_TRIG)
mso.write(":MEASure:PWIDth?")
time.sleep(TIME_SLEEP_MEAS)
delay = float(mso.read())

len_cable = delay/2*vLight
print(len_cable)

### redefine channel scale and offset
mso.write(":CHANnel1:SCALe 0.05")          # V/div
mso.write(":CHANnel1:OFFSet 0.475")

mso.write(":MEASure:CLEar")
### change time-base position
timeDiv = 50E-9
mso.write(":TIMebase:POSition " + str(delay+timeDiv)) # Décalage de la fenêtre
window_time=timeDiv*10
mso.write(f":TIM:RANG {window_time}")

time.sleep(0.5)

### acquire data from channel#1
### determine time constant (90%->10% --> 2.2RC or 63% --> RC)
### MARKER MODE/X1Position/Y1Position/VMIN/TVALue
mso.write(":MEASure:VMAX CHANnel1")
time.sleep(0.5)
mso.write(":MEASure:VMAX?")
time.sleep(TIME_SLEEP_MEAS)
v_max = float(mso.read())
mso.write(":MEASure:VMIN CHANnel1")
time.sleep(0.5)
mso.write(":MEASure:VMIN?")
time.sleep(TIME_SLEEP_MEAS)
v_min = float(mso.read())
print(v_min,v_max)

gamma = (v_max-(V_P-V_N)/2)/(V_P-V_N)/2
rL = 50*(1+gamma)/(1-gamma)
print(rL)

mso.write(":MEASure:TVALue? " + str((v_max-v_min)*0.1 + v_min) + ",+1,CHANnel1")
time.sleep(TIME_SLEEP_MEAS)
t1 = float(mso.read())

mso.write(":MEASure:TVALue? " + str(v_max-(v_max-v_min)*0.1) + ",+1,CHANnel1")
time.sleep(TIME_SLEEP_MEAS)
t2 = float(mso.read())

print(t1,t2)

time.sleep(5)

### determine time constant and capacitance value...
tau = (t2-t1)/2.2
print(tau)
c = tau/(50*rL/(50+rL))
print(c)

mso.close()

