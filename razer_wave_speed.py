# Author: Mike Cardillo, 2017
#  Email: mcardillo55@gmail.com
#   Desc: Control speed of the Razer 'wave' effect by sending custom values to
#		  the razerkbd driver and varying the sleep() time.

import pyshark
import time
import os, sys

RAZERKBD_SYSFS_PATH = '/sys/bus/hid/drivers/razerkbd/0003:1532:0221.0013/'
PCAP_FILE = '/home/mike/razer_packets.pcapng'


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

print("done analyzing")
print(len(slow_wave_pattern))

while True:
	for pattern in slow_wave_pattern:
		if pattern[0] == 0:
			with open(os.path.join(RAZERKBD_SYSFS_PATH, 'matrix_effect_custom'), 'w') as enable_custom_effect:
				enable_custom_effect.write('1')

		with open(os.path.join(RAZERKBD_SYSFS_PATH, 'matrix_custom_frame'), 'wb') as custom_frame:
			custom_frame.write(pattern)

		sys.stdout.flush()

		time.sleep(0.0010)