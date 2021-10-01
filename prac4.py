# imports
import busio
import digitalio
import board
import RPi.GPIO as GPIO 
import threading
import time
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# global variables
global start_time
global period
global modes_array
global mode_index

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 2, LDR
chan_ldr = AnalogIn(mcp, MCP.P2)

# create an analog input channel on pin 1, temp sensor
chan_temp = AnalogIn(mcp, MCP.P1)

# Defining button pin number on RPi
btn_pin = 23 # Physical pin 16, GPIO 23

# Defining sampling rate modes
modes_index = 0
modes_array = [10, 5, 1]
period = modes_array[modes_index]

# Printing the header for columns
print("Runtime\t\tTemp Reading\t\tTemp\t\tLight Reading")

# These print statements (commented out) were part of the copied code from the assignment page
# print("Raw ADC Value: ", chan_ldr.value)
# print("ADC Voltage: " + str(chan_ldr.voltage) + "V")

# Setup for button
def setup():
	GPIO.setup(btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(btn_pin, GPIO.RISING, callback=increment_index, bouncetime=250)
	pass

# Function that gets called when button is pressed, increments the index of the sampling time array (3 modes of operation)
def increment_index(self):
	global modes_index
	
	if (modes_index > 1):
		modes_index = 0
	else:
		modes_index += 1
	#print("Index is " + str(modes_index))
	pass

# Definition of thread function, it executes at a rate determined by the button on the breadboard
def output_values_thread():
	"""
	This function prints the current sensor readings to the screen (in their respective columns)
	every X number of seconds, where X is the sampling rate determined by the button
	"""
	period = modes_array[modes_index]
	#print("Period is " + str(period))
	thread = threading.Timer(period, output_values_thread)
	thread.daemon = True  # Daemon threads exit when the program does
	thread.start()
	time_now = time.time() - start_time # Determines how many seconds the program has been running for
	temp_conv = (chan_temp.voltage - 0.5)/0.01 # Conversion from volts to degrees celcius
	print(str(int(round(time_now, 0))) + "s\t" + "\t" + str(chan_temp.value) + "\t\t" + "\t" + str(round(temp_conv, 2)) + "C\t" + "\t" + str(chan_ldr.value))
	pass

# Main function execution
if __name__ == "__main__": 
	try:
		setup()
		start_time = time.time() # initializing start time (global)
		output_values_thread() # calling to start the thread
		while True:
			pass
	except Exception as e:
		print(e)
	finally:
		GPIO.cleanup()
