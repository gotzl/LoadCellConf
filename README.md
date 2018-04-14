Small tool allowing to modify the (electrical) resistance of the Load Cell in the Fanatec CSL Elite brake pedal.

Development:
A virtual machine was used to find the bytearrays used to write the resistance and interpret the received bytearray from the device.
There are some hardcoded bytes whose meaning I do not (yet) know ...

Usage:
> python LoadCellConf.py # read current value
> python LoadCellConf.py [0-10] # set value, with 0 lowest and 10 the highest resistance
