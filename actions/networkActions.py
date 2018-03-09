import os
import subprocess

networks = {}

class Network(object):
    def __init__(self, key, networkName):
        self.key = key
        self.networkName = networkName
        self.connectedContainer = {}
        self.netemInitialized = {}

    def isNetemInitialized(self, container):
        return self.netemInitialized[container]

    def setNetemInitialized(self, container, newValue):
        self.netemInitialized[container] = newValue

    def getNetworkName(self):
        return self.networkName

    def connect(self, containerName, interfaceName):
        self.netemInitialized[containerName] = False
        self.connectedContainer[containerName] = interfaceName

    def disconnect(self, containerName):
        self.connectedContainer.pop(containerName, None)

    def getConnectedContainer(self):
        return self.connectedContainer.keys()

    def getInterfaceNameOfConnectedContainer(self, containerName):
        return self.connectedContainer[containerName]

    def printNetwork(self):
        print "Network: " + self.key
        print "Network-Name: " + self.networkName
        print "Connected: "
        for container in self.connectedContainer:
            print container+" : "+self.connectedContainer[container]

def join(actionObject, dockerComposeProjectName):
    containerList = actionObject["container"]
    internal = False
    if "internal" in actionObject:
        internal = actionObject["internal"]

    mode = "cluster"
    if "mode" in actionObject:
        mode = actionObject["mode"]

    exitCode = 0
    if mode == "cluster":
        exitCode = connect(containerList, dockerComposeProjectName, internal)
    elif mode == "row" or mode == "ring":
        for i in range(0, len(containerList)-1):
            exitCode = max(connect(containerList[i:i+2], dockerComposeProjectName, internal), exitCode)

    # Close the ring
    if mode == "ring":
        exitCode = max(connect([containerList[0], containerList[len(containerList)-1]], dockerComposeProjectName, internal), exitCode)
    return exitCode

def cut(actionObject, dockerComposeProjectName):
    containerList = actionObject["container"]
    return disconnect(containerList, dockerComposeProjectName)

def deleteAllNetworks():
    exitCode = -1
    for key in networks:
        networkName = networks[key].getNetworkName()
        exitCode = max(deleteNetwork(networkName), exitCode)
    return exitCode

def delay(actionObject, dockerComposeProjectName):
    time = actionObject["time"]
    if time is None:
        print "You have to set a time"
        return 1
    arguments = [time]

    if "jitter" in actionObject:
        arguments = arguments+[actionObject["jitter"]]
        if "correlation" in actionObject:
            arguments = arguments+[actionObject["correlation"]]
        if "distribution" in actionObject:
            arguments = arguments+["distribution", actionObject["distribution"]]

    return executeNetemCommandsForNetwork(actionObject, dockerComposeProjectName, "delay", arguments)

def duplicate(actionObject, dockerComposeProjectName):
    percent = actionObject["percent"]
    arguments = [str(percent)+"%"]
    if "correlation" in actionObject:
        arguments = arguments+[actionObject["correlation"]]
    return executeNetemCommandsForNetwork(actionObject, dockerComposeProjectName, "duplicate", arguments)

def corrupt(actionObject, dockerComposeProjectName):
    percent = actionObject["percent"]
    arguments = [str(percent)+"%"]
    if "correlation" in actionObject:
        arguments = arguments+[actionObject["correlation"]]
    return executeNetemCommandsForNetwork(actionObject, dockerComposeProjectName, "corrupt", arguments)

def loss(actionObject, dockerComposeProjectName):
    percent = actionObject["percent"]
    arguments = [str(percent)+"%"]
    if "correlation" in actionObject:
        arguments = arguments+[actionObject["correlation"]]
    return executeNetemCommandsForNetwork(actionObject, dockerComposeProjectName, "loss", arguments)

def connect(containerList, dockerComposeProjectName, internal):
    containerList = convertToContainerNames(containerList, dockerComposeProjectName)
    print "connect "+str(containerList)
    mapKey = getMapKey(containerList)
    if mapKey in networks:
        print "These containers are already connected"
        return 1

    # get network name
    networkName = createNetwork(internal)
    if networkName == None:
        print "Could not create network"
        return 1

    networks[mapKey] = Network(mapKey, networkName)
    exitCode = -1
    for container in containerList:
        subprocess.call(["docker", "network", "disconnect", "none", container], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)

        preNetworkInterfaces = getNetworkInterfaces(container)
        localExitCode = subprocess.call(["docker", "network", "connect", networkName, container])
        postNetworkInterfaces = getNetworkInterfaces(container)
        interfaceName = None
        for networkInterface in postNetworkInterfaces:
            if networkInterface not in preNetworkInterfaces:
                interfaceName = networkInterface

        if localExitCode == 0 and interfaceName is not None:
            networks[mapKey].connect(container, interfaceName)
        exitCode = max(exitCode, localExitCode)

    if exitCode != 0:
        print "Could not connect all containers to the network"

    return exitCode

def disconnect(containerList, dockerComposeProjectName):
    containerList = convertToContainerNames(containerList, dockerComposeProjectName)
    print "disconnect "+str(containerList)
    mapKey = getMapKey(containerList)
    if mapKey not in networks:
        print "This network does not exists"
        return 1

    network = networks[mapKey]

    exitCode = -1
    for container in containerList:
        localExitCode = subprocess.call(["docker", "network", "disconnect", network.getNetworkName(), container])
        if localExitCode == 0:
            network.disconnect(container)
        exitCode = max(exitCode, localExitCode)

    if exitCode != 0:
        print "Could not disconnect all containers from the network"
        return 1

    exitCode = deleteNetwork(network.getNetworkName())
    if exitCode != 0:
        print "Cloud not delete the network"
    else:
        networks.pop(mapKey, None)
    return exitCode


def createNetwork(internal):
    i = 0
    networkPrefix = "network-simulator-network_"
    exitCode = 0

    # Returns 0 if network exists
    while subprocess.call(["docker", "network", "inspect", networkPrefix+str(i)], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT) == 0:
        i += 1

    if internal:
        exitCode = subprocess.call(["docker", "network", "create", "--internal", networkPrefix+str(i)])
    else:
        exitCode = subprocess.call(["docker", "network", "create", networkPrefix+str(i)])

    if exitCode == 0:
        return networkPrefix+str(i)
    return None

def deleteNetwork(networkName):
    return subprocess.call(["docker", "network", "rm", networkName])

def getNetworkInterfaces(containerName):
    proc = subprocess.Popen(["docker", "exec", containerName, "ls", "/sys/class/net"], stdout=subprocess.PIPE)
    return proc.stdout.read().split()

def convertToContainerNames(containerList, dockerComposeProjectName):
    newList = list()
    for container in containerList:
        newList.append(dockerComposeProjectName + "_" + container + "_1")
    return newList

def getMapKey(containerList):
    result = ""
    for container in sorted(containerList):
        result = result + container + ";"
    return result

def executeNetemCommandsForNetwork(actionObject, dockerComposeProjectName, command, arguments):
    networkList = convertToContainerNames(actionObject["network"], dockerComposeProjectName)
    networkKey = getMapKey(networkList)
    network = networks[networkKey]

    exitCode = -1

    for container in network.getConnectedContainer():
        localExitCode = executeNetemCommand(network, container, command, arguments)
        if localExitCode == 0:
            network.setNetemInitialized(container, True)
        exitCode = max(localExitCode, exitCode)

    return exitCode

def executeNetemCommand(network, containerName, command, arguments):
    interface = network.getInterfaceNameOfConnectedContainer(containerName)
    netemMode = None
    if not network.isNetemInitialized(containerName):
        netemMode = "add"
    else:
        netemMode = "change"
    return subprocess.call(["docker", "exec", containerName, "tc", "qdisc", netemMode, "dev", interface, "root", "netem", command] + arguments)
