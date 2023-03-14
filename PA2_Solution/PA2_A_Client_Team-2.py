#!/usr/bin/env python3

'''
Team 2
Guy Allgood
Liam Cristescu
Tomas Wahl-Diaz
Tamanna Zahir

'''

from socket import *
import select
import time
import math

def minMaxAvg(someList):               	# Borrowed this from Guy's python course final
	listMax = someList[0]				# Just annotating that as a matter of fact
	listMin = someList[0]				# so we can't be docked for plagerism.
	listSum = someList[0]
	for i in range(1,len(someList)):
		listMax = someList[i] if someList[i] > listMax else listMax
		listMin = someList[i] if someList[i] < listMin else listMin
		listSum += someList[i]
	listAverage = listSum/len(someList)
	return (listMin,listMax,listAverage)
	
def time_this():
	return time.perf_counter_ns()
	
def estRTT(samRTT): # EstimatedRTT = (1- α)*EstimatedRTT + α*SampleRTT first one set to .125
	if (len(estList) > 0):
		output = (1-0.125) * estList[-1] + 0.125 * samRTT
	else:
		output = (1-0.125) * samRTT + 0.125 * samRTT #First run cannot use empty list
	estList.append(output)
	print ("estimated_rtt = %0.3f ms, " % (output), end="", flush = True)
	devRTT(output, samRTT)
	return output

def devRTT(estRTTs, samRTT): # DevRTT = (1-β)*DevRTT + β*|SampleRTT-EstimatedRTT first one set to .25
	if (len(devList) > 0):
		output = (1-0.25) * devList[-1] + 0.25 * math.fabs(samRTT - estList[-1])
	else:
		output = 1 * (samRTT)/2		# First sample, cannot use empty list
	devList.append(output)
	print("dev_rtt = %0.3f ms" % (output))
	return output

def t_oInterval(): # TimeoutInterval = EstimatedRTT + 4*DevRTT
	return estList[-1] + 4 * devList[-1]

def sendPing(contents):
	samRTT = 0
	begin_time = 0.0
	end_time = 0.0
	serverName = '172.16.30.20' 		# My network assigned address, change to meet needs
	serverPort = 12000
	clientSocket = socket(AF_INET, SOCK_DGRAM) 		# Create socket
													# clientSocket.settimeout(1.0) cannot use this method, you can’t catch it in a try block.
	clientSocket.sendto(contents.encode(), (serverName, serverPort)) 	# Send request to the server.
													# Following code allows us to set a timeout (1 sec), and catch it in a try block via operating system calls.
	if contents != "abcdefgh": 						# ignore first run, contaminates the results by
		begin_time = time_this()					# added time for ARP calls etc.
	incoming = select.select([clientSocket],[],[],1.0) 	# Use of select.select is to poll the OS, and 														return a list containing below message with a 														timeout of 1 second as the last argument.
	try:
		modifiedMessage, serverAddress = incoming[0][0].recvfrom(2048)
		if contents != "abcdefgh": 					# ignore first run, contaminates the results
			end_time = time_this()					# need timers for samRTTs
			samRTT = (end_time - begin_time) / 1000000 # convert from nanoseconds
			samList.append(samRTT)						# stores samples for statistics
	except IndexError:
		if contents != "abcdefgh": 						# ignore first run, contaminates the results
			print("Request timed out") 					# Catch OS enforced timeout
	finally :
		if ((contents != "abcdefgh") & (samRTT != 0)):	# again ignoring first ping to smooth calculations
			print("sample_rtt = %0.3f ms, " % (samRTT), end="", flush = True) # Moved from try block to avoid making function calls within the try.  If functions fail, the try fires.
			estRTT(samRTT) # again moved from try block.
			
#  This begins the main function, initializes lists, sets firstRun boolean to to Try so adjustments can be made.
samList = []
devList = []
estList = []
firstRun = True

# Following values are just to send different payloads in testing to see if there's any practical effect on size of payload.
bytes_08 = "abcdefgh" # use this to initialize the data path, smooth the output, avoid ARP and other initializing problems
bytes_16 = "abcdefghijklmonp"
bytes_32 = "abcdefghijklmnopqrstuvwxyzabcdef"
bytes_64 = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijkl"  # This is the payload of the ping, which I didn't do any sanity checking, but could be added later.

# send 10 pings
for numPings in range(0,10):
	if firstRun:
		sendPing(bytes_08) # signal to initialize communications, remove ARP and any other items from calculations.
		firstRun = False
	print("Ping %d: " % (numPings+1), end="", flush=True) # Keep print statement on same line for appending in method
	sendPing(bytes_64)
	
# Calculate ending values in print statement
print("\nSummary values:\n\tmin_rtt = %0.3f ms\n\tmax_rtt = %0.3f ms\n\tavg_rtt = %0.3f ms" % (minMaxAvg(samList)))
print("\tPacket loss: %0.2f%%" % ((10 - len(samList)) * 10), end="", flush=True)
print ("\n\tTimeout Interval: %0.3f ms" % (t_oInterval()))

'''
						Sample runs	
				These check out in the spreadsheet
Ping 1: sample_rtt = 0.793 ms, estimated_rtt = 0.793 ms, dev_rtt = 0.397 ms
Ping 2: sample_rtt = 0.595 ms, estimated_rtt = 0.769 ms, dev_rtt = 0.341 ms
Ping 3: sample_rtt = 0.435 ms, estimated_rtt = 0.727 ms, dev_rtt = 0.329 ms
Ping 4: sample_rtt = 0.431 ms, estimated_rtt = 0.690 ms, dev_rtt = 0.311 ms
Ping 5: Request timed out
Ping 6: sample_rtt = 0.840 ms, estimated_rtt = 0.709 ms, dev_rtt = 0.266 ms
Ping 7: sample_rtt = 0.831 ms, estimated_rtt = 0.724 ms, dev_rtt = 0.226 ms
Ping 8: sample_rtt = 1.838 ms, estimated_rtt = 0.863 ms, dev_rtt = 0.414 ms
Ping 9: sample_rtt = 0.621 ms, estimated_rtt = 0.833 ms, dev_rtt = 0.363 ms
Ping 10: sample_rtt = 0.544 ms, estimated_rtt = 0.797 ms, dev_rtt = 0.336 ms

Summary values:
	min_rtt = 0.431 ms
	max_rtt = 1.838 ms
	avg_rtt = 0.770 ms
	Packet loss: 10.00%
	Timeout Interval: 2.139 ms

Ping 1: sample_rtt = 0.871 ms, estimated_rtt = 0.871 ms, dev_rtt = 0.435 ms
Ping 2: sample_rtt = 0.869 ms, estimated_rtt = 0.871 ms, dev_rtt = 0.327 ms
Ping 3: sample_rtt = 0.865 ms, estimated_rtt = 0.870 ms, dev_rtt = 0.247 ms
Ping 4: Request timed out
Ping 5: sample_rtt = 0.752 ms, estimated_rtt = 0.855 ms, dev_rtt = 0.211 ms
Ping 6: sample_rtt = 0.438 ms, estimated_rtt = 0.803 ms, dev_rtt = 0.249 ms
Ping 7: Request timed out
Ping 8: Request timed out
Ping 9: sample_rtt = 0.793 ms, estimated_rtt = 0.802 ms, dev_rtt = 0.189 ms
Ping 10: sample_rtt = 0.556 ms, estimated_rtt = 0.771 ms, dev_rtt = 0.196 ms

Summary values:
	min_rtt = 0.438 ms
	max_rtt = 0.871 ms
	avg_rtt = 0.735 ms
	Packet loss: 30.00%
	Timeout Interval: 1.553 ms

'''
