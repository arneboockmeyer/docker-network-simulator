from actions.containerActions import startContainer, stopContainer, restartContainer
from actions.timerActions import startTimer, stopTimer, printTimer
from actions.networkActions import join, cut, delay, duplicate, corrupt, loss

def executeAction(action, actionObject, dockerComposeFilename, dockerComposeProjectName):
    if action == "join":
        return join(actionObject, dockerComposeProjectName)
    elif action == "cut":
        return cut(actionObject, dockerComposeProjectName)
    elif action == "startContainer":
        return startContainer(actionObject, dockerComposeFilename, dockerComposeProjectName)
    elif action == "stopContainer":
        return stopContainer(actionObject, dockerComposeFilename, dockerComposeProjectName)
    elif action == "restartContainer":
        return restartContainer(actionObject, dockerComposeFilename, dockerComposeProjectName)
    elif action == "startTimer":
        return startTimer(actionObject)
    elif action == "stopTimer":
        return stopTimer(actionObject)
    elif action == "printTimer":
        return printTimer(actionObject)
    elif action == "delay":
        return delay(actionObject, dockerComposeProjectName)
    elif action == "duplicate":
        return duplicate(actionObject, dockerComposeProjectName)
    elif action == "corrupt":
        return corrupt(actionObject, dockerComposeProjectName)
    elif action == "loss":
        return loss(actionObject, dockerComposeProjectName)
