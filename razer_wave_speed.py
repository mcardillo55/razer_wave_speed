# Author: Mike Cardillo, 2017
#  Email: mcardillo55@gmail.com
#   Desc: Control speed of the Razer 'wave' effect by sending custom values to
#         the razerkbd driver and varying the sleep() time.


import time
import os, sys
import pickle

RAZERKBD_SYSFS_PATH = '/sys/bus/hid/drivers/razerkbd/0003:1532:0221.0013/'
PCAP_FILE = '/home/mike/razer_packets.pcapng'

if os.path.isfile('razr_wave_data.dat'):
    print("using pickle")
    with open('razr_wave_data.dat', 'rb') as wave_data:
        slow_wave_pattern = pickle.load(wave_data)
else:
    import pyshark
    
    print('analyzing')
    cap = pyshark.FileCapture(PCAP_FILE)

    slow_wave_pattern = []

    for idx, cur_cap in enumerate(cap):
        if idx == 966:
            # This is when the pattern repeats.
            break
        cap_data = cur_cap.data.usb_data_fragment
        if cap_data.binary_value[8] == 255:
            # First 8 bytes are control bytes and not included
            # Next are row index, row start and row stop
            # Then 22 RGB values
            slow_wave_pattern.append(cap_data.binary_value[9:78])
    with open('razr_wave_data.dat', 'wb') as wave_data:
        pickle.dump(slow_wave_pattern, wave_data)

while True:
    pattern_cat = b''

    for pattern in slow_wave_pattern:
        # Concatinate all 6 rows into one, in order to minimize opening sysfs node
        pattern_cat += pattern
        if pattern[0] == 5:
            with open(os.path.join(RAZERKBD_SYSFS_PATH, 'matrix_custom_frame'), 'wb') as custom_frame:
                custom_frame.write(pattern_cat)
            pattern_cat = b''
            with open(os.path.join(RAZERKBD_SYSFS_PATH, 'matrix_effect_custom'), 'w') as enable_custom_effect:
                enable_custom_effect.write('1')
            sys.stdout.flush()

        time.sleep(0.005)
