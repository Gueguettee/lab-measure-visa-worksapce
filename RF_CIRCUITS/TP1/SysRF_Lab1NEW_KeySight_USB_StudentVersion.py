#import visa
import pyvisa as visa
import time
import string

rm = visa.ResourceManager()
## cable between GenOut and Channel #1
## cable under test between Channel 1 and 2
## button "Utility" > "I/O" > copy VISA adress
mso=rm.open_resource("USB0::10893::6000::MY55440261::INSTR")
mso.write("*IDN?")
print(mso.read())
mso.write("*RST")
mso.write("*CLS")

### CHANNELS settings
window_time=600E-9
# set timebase range to window_time
# set timebase reference to left

# display only channels 1 & 2
# set both channel scale to 0.2V
# set both channel offset to 0.5V
# set both channel impedance to high-impedance


### WAVEFORM GENERATOR settings
# define a square wavefor, frequency 50kHz, between 0V and 1V
# activate the generator output

### TRIGGER setttings
# set trigger to channel 1, at 0.25V

### DELAY MEASUREMENT settings
time.sleep(3)
mso.write(":DIGitize")
mso.write(":MEASure:DELay CHANnel1,CHANnel2")
mso.write(":MEASure:DEFine DELay,+1,+1")
mso.write(":MEASure:DELay?")
ddelay=mso.read()
print("Line delay = "+str(ddelay))
ddelay=ddelay[0:len(ddelay)-1]

# evaluate cable length and print it

### MARKERS settings
time.sleep(1)
# use :MARKer command to evaluate signal amplitudes
# calculate the reflection coefficient
# calculate the load resistance and put in "Rload" variable

time.sleep(1)


################  Create LTSpice file
ff=open('delayline.cir','w')
ff.write('* delay line model\n')
ff.write('T1 a 0 b 0 Td='+ddelay+' Z0=50\n')
ff.write('V1 a 0 PWL file=delayline_trace1.txt\n')
ff.write('V2 b_meas 0 PWL file=delayline_trace2.txt\n')
if gamm<1:
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
ff=open('delayline_trace1.txt','w')
for x in range(1,cnt):
    ff.write(str(x*step)+'\t'+data[x]+'\n')
ff.close()

#do the same for channel 2

mso.close()
