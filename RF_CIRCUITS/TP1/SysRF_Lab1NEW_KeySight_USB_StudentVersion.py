#import visa
import pyvisa as visa
import time
import string

vLight = 2e8

rm = visa.ResourceManager()
## cable between GenOut and Channel #1
## cable under test between Channel 1 and 2
## button "Utility" > "I/O" > copy VISA adress
mso=rm.open_resource("USB0::10893::6000::MY55440269::INSTR")
mso.write("*IDN?")
print(mso.read())
mso.write("*RST")
mso.write("*CLS")

### CHANNELS settings
window_time=1500E-9
# set timebase range to window_time
mso.write(f":TIM:RANG {window_time}")
# set timebase reference to left
mso.write(f":TIM:REF LEFT")

# display only channels 1 & 2
mso.write(":CHAN1:DISP ON")
mso.write(":CHAN2:DISP ON")
# set both channel scale to 0.2V
mso.write(":CHAN1:SCAL 0.2")
mso.write(":CHAN2:SCAL 0.2")
# set both channel offset to 0.5V
mso.write(":CHAN1:OFFS 0.5")
mso.write(":CHAN2:OFFS 0.5")
# set both channel impedance to high-impedance
mso.write(":CHAN1:IMP ONEM")
mso.write(":CHAN2:IMP ONEM")


### WAVEFORM GENERATOR settings
# define a square wavefor, frequency 50kHz, between 0V and 1V
mso.write(":WGEN:FUNCtion SQU")
mso.write(":WGEN:FREQ 50000")
mso.write(":WGEN:VOLT 1")
mso.write(":WGEN:VOLT:OFFS 0.5")
# activate the generator output
mso.write(":WGEN:OUTPut ON")

### TRIGGER setttings
# set trigger to channel 1, at 0.25V
mso.write(":TRIG:SOUR CHAN1")
mso.write(":TRIG:LEV 0.25")

### DELAY MEASUREMENT settings
time.sleep(3)
mso.write(":DIGitize")  # stop run
mso.write(":MEASure:DELay CHANnel1,CHANnel2")
mso.write(":MEASure:DEFine DELay,+1,+1")
mso.write(":MEASure:DELay?")
ddelay=mso.read()
print("Line delay = "+str(ddelay))
ddelay=ddelay[0:len(ddelay)-1]

# evaluate cable length and print it
cableLength = float(ddelay) * vLight
print("Cable length = "+str(cableLength))

### MARKERS settings
time.sleep(1)
# use :MARKer command to evaluate signal amplitudes
mso.write(":MARKer:X1Position?")
x1pos=float(mso.read())
mso.write(":MARKer:X2Position?")
x2pos=float(mso.read())

time.sleep(2)
# calculate the reflection coefficient
mso.write(":MARKer:MODE WAVeform")
mso.write(":MARKer:X1Y1source CHANnel1")
mso.write(":MARKer:X2Y2source CHANnel2")

mso.write(":MARKer:X1Position "+str(x1pos+(x2pos-x1pos)/4))
time.sleep(1)
mso.write(":MARKer:Y1Position?")
valInit=float(mso.read())
print(f"Amplitude initialisation : {valInit}")

mso.write(":MARKer:X1Position "+str(0.45*window_time))
time.sleep(1)
mso.write(":MARKer:Y1Position?")
valFinal=float(mso.read())
print(f"Amplitude finale : {valFinal}")
# calculate the load resistance and put in "Rload" variable
gamma=(valFinal-valInit)/valInit
print("Reflection coefficient = "+str(gamma))
if gamma<1:
    Rload=50*(1+gamma)/(1-gamma)
    print("Rload = "+str(Rload))

time.sleep(1)


################  Create LTSpice file
ff=open('RF_circuits/TP1/delayline.cir','w')
ff.write('* delay line model\n')
ff.write('T1 a 0 b 0 Td='+ddelay+' Z0=50\n')
ff.write('V1 a 0 PWL file=delayline_trace1.txt\n')
ff.write('V2 b_meas 0 PWL file=delayline_trace2.txt\n')
if gamma<1:
    ff.write('Rl 0 b '+str(Rload)+'\n')
ff.write('.tran '+str(0.6*window_time)+'\n')
ff.write('.backanno\n')
ff.write('.end\n')
ff.close()

################ Acquire waveforms
mso.write(":WAVeform:FORMat ASCii")
# <preamble_block> ::=  <format 16-bit NR1>,<type 16-bit NR1>,<points 32-bit NR1>,<count 32-bit NR1>,<xincrement 64-bit floating point NR3>,<xorigin 64-bit floating point NR3>,
#                       <xreference 32-bit NR1>,<yincrement 32-bit floating point NR3>,<yorigin 32-bit floating point NR3>,<yreference 32-bit NR1>
mso.write(":WAVeform:PREamble?")
preamble=mso.read().split(',')
step=float(preamble[4])     # xincrement
cnt=int(preamble[2])        # points

#### channel 1 acquisition
mso.write(":WAVeform:SOURce CHANnel1")
mso.write(":WAVeform:DATA?")
data=mso.read().split(',')
ff=open('RF_circuits/TP1/delayline_trace1.txt','w')
for x in range(1,cnt):
    ff.write(str(x*step)+'\t'+data[x]+'\n')
ff.close()

#do the same for channel 2
mso.write(":WAVeform:SOURce CHANnel2")
mso.write(":WAVeform:DATA?")
data=mso.read().split(',')
ff=open('RF_circuits/TP1/delayline_trace2.txt','w')
for x in range(1,cnt):
    ff.write(str(x*step)+'\t'+data[x]+'\n')
ff.close()

mso.close()
