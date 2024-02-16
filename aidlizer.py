#!/usr/bin/env python3
import re
import os
import sys
import getopt
import shutil

inputfile = ''
outputfile = ''
try:
    opts, args = getopt.getopt(sys.argv[1:],"hi:o:",["ifile=","ofile="])
except getopt.GetoptError:
    print (sys.argv[0] + " -i <inputfile> -o <outputfile>")
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print (sys.argv[0] + " -i <inputfile> -o <outputfile>")
        print ("Where <inputfile> is a file containing the output of both 'ps -ef' and 'dumpsys --pid --clients' from an Android target")
        sys.exit()
    elif opt in ("-i", "--ifile"):
        inputfile = arg
    elif opt in ("-o", "--ofile"):
        outputfile = arg

if inputfile == "":
    print ("Missing input file")
    print (sys.argv[0] + " -i <inputfile> -o <outputfile>")
    sys.exit(2)

foundPidTable = False
pidToName = {}

# The input file containing the output from a 'dumpsys --pid --clients' and a 'ps -ef' will be read twice.
# to keep the parseing of the two sections independent.
# Remember to do a adb root before the dumpsys and ps -ef

#
# Step 1. Read and parse the process ids and corresponding process names from 'ps -ef'
#
with open(inputfile) as file_object:
    for line in file_object:
        line = line.rstrip()
        matchPidHead = re.match(r' *UID *PID .*CMD', line)
        if matchPidHead:
            foundPidTable = True
        else:
            matchPidLine = re.match(r'[^ ]+ +(\d+) +.* \d\d:\d\d:\d\d (.+) *', line)
            if matchPidLine and foundPidTable:
                pidName = matchPidLine.group(2).split(" ")[0]
                if pidName == 'servicemanager':
                    servicemanagerPid = matchPidLine.group(1)
                pidToName[matchPidLine.group(1)] = pidName
            else:
                foundPidTable = False

#print(pidToName)
#
# Step 2. Read interfaces and server + client process ids from 'dumpsys'
#
AIDLTable = []
found=0
with open(inputfile) as file_object:
    for line in file_object:
        line = line.rstrip()
        match1 = re.match(r'DUMP OF SERVICE (.+):', line)
        match2 = re.match(r'Service host process PID: (\d+)', line)
        match3 = re.match(r'Client PIDs: (.+)', line)
        if match1:
            foundName = match1.group(1)
            found=1
        elif found == 1 and match2:
            foundPid = match2.group(1)
            found=2
        elif found == 2 and match3:
            AIDLTable.append((foundName, foundPid, match3.group(1)))
            found = 0
            foundName = ""
            foundPid = ""

#print(AIDLTable)
#
# Generating the the output
#

if outputfile != "":
    sys.stdout = open(outputfile, "w")

print("digraph aidl {")
print("    graph [rankdir = \"LR\"];")
print("    node [shape=box];")

for AIDLService in AIDLTable:
    if True:
        serviceName = AIDLService[0]
        _server = pidToName.get(str(AIDLService[1]))
        clients = AIDLService[2:][0].split(",")
        if clients.count(servicemanagerPid) > 0:
            clients.remove(servicemanagerPid)
        if clients.count('') > 0:
            clients.remove('')
        if len(clients) == 0:
            # If no clients for a service just create an arrow to self
            print("    \"" + _server + "\" -> \"" + _server + "\" [label=\"" + serviceName + "\"];")
        else:
            for client in clients:
                _client = pidToName.get(str(client))
                if _client == None:
                    continue
                print("    \"" + _client + "\" -> \"" + _server + "\" [label=\"" + serviceName + "\"];")

print("}")

sys.stdout = sys.__stdout__

if outputfile != "" and shutil.which("dot") == None:
    print("Graphviz dot not found. Install it.")
    print("Now run Graphviz dot:")
    print("dot -Tpng " + outputfile + " -o <mygraphfile>.png")
    print("Change -Tpng to -Tsvg for scalable vector graphics.")

if outputfile != "" and shutil.which("dot") != None:
    os.system("dot -Tsvg " + outputfile + " -o " + outputfile + ".svg")
    print("Created " + outputfile + ".svg")
    os.system("rm " + outputfile)
