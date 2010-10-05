import VisionEgg
from VisionEgg.DaqLPT import raw_lpt_module
import time


LPT1 = VisionEgg.DaqLPT.LPTDevice(0x379) # address of parallel port -- make sure your computer agrees

#print LPT1

#time.sleep(1.0) # wait % second

# turn all pins on
#data = 0xFF # values to output on parallel port
#raw_lpt_module.out(LPT1,data)

for i in range(5000):
	input_value = raw_lpt_module.inp(0x379) & 0x20
	print input_value
	print int(input_value)
	time.sleep(0.001)


#print data

# turn all pins on

#data = raw_lpt_module.inp(LPT1)



#print data

