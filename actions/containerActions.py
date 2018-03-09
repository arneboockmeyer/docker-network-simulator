from subprocess import call

def startContainer(actionObject, dockerComposeFilename, dockerComposeProjectName):
    print "start container "+str(actionObject)
    exitCode = -1
    for containerID in actionObject:
        exitCode = max(call(["docker-compose", "-p", dockerComposeProjectName, "-f", dockerComposeFilename, "start", containerID]), exitCode)
    return exitCode

def stopContainer(actionObject, dockerComposeFilename, dockerComposeProjectName):
    print "stop container "+str(actionObject)
    exitCode = -1
    for containerID in actionObject:
        exitCode = max(call(["docker-compose", "-p", dockerComposeProjectName, "-f", dockerComposeFilename, "stop", containerID]), exitCode)
    return exitCode

def restartContainer(actionObject, dockerComposeFilename, dockerComposeProjectName):
    print "restart container "+str(actionObject)
    exitCode = -1
    for containerID in actionObject:
        exitCode = max(call(["docker-compose", "-p", dockerComposeProjectName, "-f", dockerComposeFilename, "restart", containerID]), exitCode)
    return exitCode
