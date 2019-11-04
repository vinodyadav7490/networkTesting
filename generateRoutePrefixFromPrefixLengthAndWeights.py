#!/usr/bin/env python3

'''
Input:
   startIpAddress: 20.0.0.0
   count: 10000
   prefixLenght: 23

'''
from netaddr import IPNetwork, IPAddress
import os.path
import logging


def generateIpv4PrefixRange(startIpPrefix, count, excludeRange=None):
   ipPreficListWithPrefixLenghtAsKey = {}
   ipPreficListWithPrefixList = []

   addr = 1
   startPrefix = IPNetwork( startIpPrefix )
   mask = startPrefix.prefixlen
   ipPreficListWithPrefixLenghtAsKey[str(mask)] = []
   i=0
   while(i < count):
      startPrefix.value += ((1 ** (32 - int( startPrefix.prefixlen ))) * addr)
      #add a check to make sure that we are skiping the exluded range
      if excludeRange:
         if _isIpPrefixInRange(startPrefix, excludeRange):
            i = i-1
            #print("skiping prefix: %s" %str(startPrefix))
            subnet = startPrefix.next( )
            startPrefix = IPNetwork( subnet )
            continue
         else:pass

      ipPreficListWithPrefixLenghtAsKey[str(mask)].append(str(startPrefix.ip))
      ipPreficListWithPrefixList.append(str(startPrefix.ip))

      subnet = startPrefix.next( )
      startPrefix = IPNetwork( subnet )
      i = i + 1
   newStartPrefix = startPrefix
   return ipPreficListWithPrefixList, newStartPrefix

def generateIpv6PrefixRange(startIpPrefix, count, excludeRange=None):
   ipPreficListWithPrefixLenghtAsKey = { }
   ipPreficListWithPrefixList = []
   addr = 1
   startPrefix = IPNetwork( startIpPrefix )
   mask = startPrefix.prefixlen
   ipPreficListWithPrefixLenghtAsKey[str( mask )] = []
   i = 0
   while (i < count):
      print( count )
      startPrefix.value += ((1 ** (128 - int( startPrefix.prefixlen ))) * addr)
      # add a check to make sure that we are skiping the exluded range
      if excludeRange:
         if _isIpPrefixInRange(startPrefix, excludeRange):
            i = i - 1
            #print( "skiping prefix: %s" % str( startPrefix ) )
            subnet = startPrefix.next( )
            startPrefix = IPNetwork( subnet )
            continue
         else:
            pass

      ipPreficListWithPrefixLenghtAsKey[str( mask )].append( str( startPrefix.ip ) )
      ipPreficListWithPrefixList.append( str( startPrefix.ip ) )
      subnet = startPrefix.next( )
      startPrefix = IPNetwork( subnet )
      i = i + 1
   newStartPrefix = startPrefix
   return ipPreficListWithPrefixLenghtAsKey , newStartPrefix

def _isIpPrefixInRange(ip, excludeRange):
   a = IPNetwork(ip)
   b = IPNetwork(excludeRange)

   if (a in b) or (b in a):
      return True
   else:
      return False

def createIpPrefixInIxiaForamt(filePath, ipPreficListWithPrefixLenghtAsKey, count):
   #   Network               Next Hop            Metric LocPrf   Weight   Path
   #*>e0.0.0.0/1             192.168.1.2                     0      0      123 456 i
   # can get rid of this *,>,e
   #
   header = "Network               Next Hop            Metric LocPrf   Weight   Path\n"
   nextHop  =  '1.1.1.32'
   metric   =  '10'
   locPrf   =  '100'
   weight   =  '100'
   path     =  '100 101'
   f = open(filePath, 'w')
   f.write(header)

   for key in ipPreficListWithPrefixLenghtAsKey:
      count = len(ipPreficListWithPrefixLenghtAsKey[key])
      for i in range(count):
         #build the cmd/string here
         ntwk = ipPreficListWithPrefixLenghtAsKey[key][i]
         cmdstring = ntwk + "  " + nextHop + "   " + metric + "  " + locPrf + "  " + weight + "  " + path + "\n"

         f.write(cmdstring)
         print("Open a file and start adding the ip address")

   return None

def getAllPrefixList(paramDict, entireDict):
   ipv4PreficListWithPrefixLenghtAsKey= {}
   ipv6PreficListWithPrefixLenghtAsKey = {}

   #some how I have to get IP Prefix list for all the prefix in one dict
   #prefix distribution is based on weight
   #one thing we can do is based on total count and prefix get the totalcount for each prefix
   #Then call "generateIpv4PrefixRange" or "v6" for each prefix
   #then combine all the o/p and vallah done dona done

   #loop to get the count for each prefix based on weight and total count
   totalV4Count   =  entireDict['RouteScale']['totalCount']['v4']
   totalV6Count   =  entireDict['RouteScale']['totalCount']['v6']

   #check if total of all the weights are 100 or not

   v4PrefixWeightDict  =  entireDict['RouteScale']['Weights']['v4']
   v6PrefixWeightDict  =  entireDict['RouteScale']['Weights']['v6']

   weightSum=0
   for item in v4PrefixWeightDict:
      weightSum = weightSum + v4PrefixWeightDict[item]
   if weightSum == 100:
      logging.error("Please make sure sum of all the prefix weight for v4 are 100")

   weightSum = 0
   for item in v6PrefixWeightDict:
      weightSum = weightSum + v6PrefixWeightDict[item]
   if weightSum == 100:
      logging.error( "Please make sure sum of all the prefix weight for v6 are 100" )

   #get start and excludeRange
   excludev4Range = entireDict['RouteScale']['ExcludeIprange']['v4']
   excludev6Range = entireDict['RouteScale']['ExcludeIprange']['v6']
   startIpv4Prefix = entireDict['RouteScale']['StartIpPrefix']['v4']
   startIpv6Prefix = entireDict['RouteScale']['StartIpPrefix']['v6']

   newStartIpv4Prefix   = startIpv4Prefix
   newStartIpv6Prefix   =  startIpv6Prefix

   for prefix in v4PrefixWeightDict:
      totalCount = int((int(v4PrefixWeightDict[prefix]) / 100) * totalV4Count)
      #call "v4 and v6 generateIpPrefix" method here
      ipv4PreficListWithPrefixLenghtAsKey[prefix], newStartIpv4Prefix = generateIpv4PrefixRange( startIpPrefix=newStartIpv4Prefix, count=totalCount, excludeRange=excludev4Range )

   for prefix in v6PrefixWeightDict:
      totalCount = int( (int( v6PrefixWeightDict[prefix] ) / 100) * totalV4Count )
      ipv6PreficListWithPrefixLenghtAsKey[prefix], newStartIpv6Prefix = generateIpv6PrefixRange(startIpPrefix=newStartIpv6Prefix, count=totalCount, excludeRange=excludev6Range)

   return ipv4PreficListWithPrefixLenghtAsKey

def mainFuction(entireDict):
   '''
   :param entireDict:
   :return:
   '''
   currentPath = os.path.expanduser()
   scriptName = os.path.basename( __file__ )
   currentPath = currentPath+"\\"+scriptName
   ipPreficListWithPrefixLenghtAsKey = getAllPrefixList(entireDict)

   try:
      open(currentPath, 'w+')
      createIpPrefixInIxiaForamt(currentPath, ipPreficListWithPrefixLenghtAsKey)
   except Exception as e:
      logging.warning("error while opening the file: %s" %currentPath)

   return None
