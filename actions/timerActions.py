import time

currentTimers = {}
current_milli_time = lambda: int(round(time.time() * 1000))

def startTimer(actionObject):
    for identifier in actionObject:
        currentTimers[identifier] = current_milli_time()
        print "started timer "+identifier
    return 0

def stopTimer(actionObject):
    exitCode = -1
    for identifier in actionObject:
        exitCode = max(printSingleTimer(identifier), exitCode)
        currentTimers.pop(identifier, 0)
    return exitCode

def printTimer(actionObject):
    exitCode = -1
    for identifier in actionObject:
        exitCode = max(printSingleTimer(identifier), exitCode)
    return exitCode

def printSingleTimer(timerIdentifier):
    if timerIdentifier not in currentTimers:
        print "Timer " + timerIdentifier + " not found!"
        return 1
    else:
        print timerIdentifier + ": " + str((current_milli_time() - currentTimers[timerIdentifier]))
        return 0
