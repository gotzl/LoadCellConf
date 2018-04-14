import sys
import usb1

VENDOR_ID = 0x0eb7
DEVICE_ID = 0x6204


def usage():
    print("Usage: python fanatec_lc.py [0-10]")
    sys.exit(0)


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
            handle.interruptWrite(0x01, bytearray.fromhex('f8090106000000'))
            current_val = handle.interruptRead(0x81, 16)[-4]

            # print the current value
            if val is None:
                print('Current value: %i'%(current_val-1))
                sys.exit(1)

            # only write the new value if it's different from the current value
            elif current_val != val:
                handle.interruptWrite(0x01, bytearray.fromhex('f80901160%x0000'%val))
                handle.interruptRead(0x81, 16)