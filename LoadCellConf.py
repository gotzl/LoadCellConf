import sys
import usb1

VENDOR_ID = 0x0eb7
DEVICE_ID = 0x6204

CMD_GET_STATE = 0x06
CMD_DISABLE_AUTOCALIB = 0x13
CMD_ENABLE_AUTOCALIB = 0x14
CMD_SET_MINMAX = 0x15
CMD_SET_RESISTANCE = 0x16
AXIS_GAS = 0x0
AXIS_BREAK = 0x1
AXIS_CLUTCH = 0x2
AXIS_MIN = 0x0
AXIS_MAX = 0x1


def usage():
    print("Usage: python LoadCellConf.py [0-10]")
    sys.exit(0)


def payload(*args):
    p = bytearray.fromhex('f80901')
    p.extend(args)
    # pad with zeros
    p.extend([0]*(7-len(p)))
    return p


if __name__ == '__main__':
    if len(sys.argv)>3: usage()
    val = None
    if len(sys.argv)==2:
        val = int(sys.argv[1])
        if val < 0 or val > 10: usage()
        val += 1 # actual value has an offset of 1

    with usb1.USBContext() as context:
        handle = context.openByVendorIDAndProductID(
            VENDOR_ID,
            DEVICE_ID,
            skip_on_error=True,
        )
        if handle is None:
            print('Device not found')
            sys.exit(1)

        handle.setAutoDetachKernelDriver(True)
        with handle.claimInterface(0):
            # request reading of current value
            handle.interruptWrite(0x01, payload(CMD_GET_STATE))
            ret = handle.interruptRead(0x81, 16)
            current_val = ret[-4]
            mode = ret[-5]

            # check if auto calibration mode is set
            if mode == 0xff:
                # toggle autocalibration mode
                print('Setting to autocalibration mode')
                handle.interruptWrite(0x01, payload(CMD_ENABLE_AUTOCALIB))
                # handle.interruptWrite(0x01, payload(CMD_GET_STATE))
                if handle.interruptRead(0x81, 16)[-5] != 0:
                    print('Could not set to autocalibration mode')
                    sys.exit(1)

            # print the current value
            if val is None:
                print('Current value: %i'%(current_val-1))
                sys.exit(1)

            # only write the new value if it's different from the current value
            elif current_val != val:
                handle.interruptWrite(0x01, payload(CMD_SET_RESISTANCE, val))
                handle.interruptRead(0x81, 16)

            ## in manual mode
            # set current state max gas: f8090115000100
            # set current state min gas: f8090115000000
            # set current state max clutch: f8090115020100
            # set current state min clutch: f8090115020000