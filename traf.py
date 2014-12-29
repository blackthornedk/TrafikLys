from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp, udp6
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api
from time import time, sleep
import serial

# Serial port to write to
serialPort = '/dev/cuaU0'
serialSpeed = 9600

# SNMP host to poll
snmpHost = '192.168.220.254'
snmpCommunity = 'public'

# Data OIDs to read. (On a Juniper SRX240)
ifHCIn1SecRate = '1.3.6.1.4.1.2636.3.3.1.1.7.510'
ifHCOut1SecRate = '1.3.6.1.4.1.2636.3.3.1.1.8.510'

# Global status variables.
inRate = 0
outRate = 0

# Open Serial Port
ser = serial.Serial(serialPort, serialSpeed)

# Protocol version to use
pMod = api.protoModules[api.protoVersion2c]

# Build PDU
reqPDU =  pMod.GetRequestPDU()
pMod.apiPDU.setDefaults(reqPDU)
pMod.apiPDU.setVarBinds(
    reqPDU, ( (ifHCIn1SecRate, pMod.Null('')),
              (ifHCOut1SecRate, pMod.Null('')) )
    )

# Build message
reqMsg = pMod.Message()
pMod.apiMessage.setDefaults(reqMsg)
pMod.apiMessage.setCommunity(reqMsg, snmpCommunity)
pMod.apiMessage.setPDU(reqMsg, reqPDU)

startedAt = time()

def cbTimerFun(timeNow):
    if timeNow - startedAt > 3:
        raise Exception("Request timed out")
    
def cbRecvFun(transportDispatcher, transportDomain, transportAddress,
              wholeMsg, reqPDU=reqPDU):
    global inRate, outRate
    while wholeMsg:
        rspMsg, wholeMsg = decoder.decode(wholeMsg, asn1Spec=pMod.Message())
        rspPDU = pMod.apiMessage.getPDU(rspMsg)
        # Match response to request
        if pMod.apiPDU.getRequestID(reqPDU)==pMod.apiPDU.getRequestID(rspPDU):
            # Check for SNMP errors reported
            errorStatus = pMod.apiPDU.getErrorStatus(rspPDU)
            if errorStatus:
                print(errorStatus.prettyPrint())
            else:
                for oid, val in pMod.apiPDU.getVarBinds(rspPDU):
                    if oid.prettyPrint()==ifHCIn1SecRate:
                        inRate = val
                    if oid.prettyPrint()==ifHCOut1SecRate:
                        outRate = val
            transportDispatcher.jobFinished(1)
    return wholeMsg


def readCounters():
    global startedAt
    startedAt = time()

    transportDispatcher = AsynsockDispatcher()

    transportDispatcher.registerRecvCbFun(cbRecvFun)
    transportDispatcher.registerTimerCbFun(cbTimerFun)

    # UDP/IPv4
    transportDispatcher.registerTransport(
        udp.domainName, udp.UdpSocketTransport().openClientMode()
    )

    # Pass message to dispatcher
    transportDispatcher.sendMessage(
        encoder.encode(reqMsg), udp.domainName, (snmpHost, 161)
    )
    transportDispatcher.jobStarted(1)

    # Dispatcher will finish as job#1 counter reaches zero
    transportDispatcher.runDispatcher()

    transportDispatcher.closeDispatcher()

    # Rate in bytes / sec
    print('In Rate: %s Out Rate: %s' % (inRate, outRate))

    # Rate in MB / sec
    inRateMB = inRate / (1024 ** 2) 
    outRateMB = outRate / (1024 ** 2) 
    print('In Rate: %s Out Rate: %s' % (inRateMB, outRateMB))

    # Rate in LED's lit
    inRateInt = inRateMB / 62.5
    outRateInt = outRateMB / 62.5
    print('In Rate: %s Out Rate: %s' % (inRateInt, outRateInt))

    # We only have one row of LEDs. Take the highest rate.
    counter = inRateInt if inRateInt > outRateInt else outRateInt
    print('Setting LED Value: %s' % counter)
    ser.write('q%s' % counter)

# Main application Loop
while True:
    readCounters()
    sleep(5.0)
