import threading
import time
from subprocess import call
from executeAction import executeAction

class eventWorker (threading.Thread):
    def __init__(self, eventKey, eventObject, dockerComposeFilename, dockerComposeProjectName, threadMap, threadFinishedMap):
        threading.Thread.__init__(self)
        self.eventKey = eventKey
        self.eventObject = eventObject
        self.dockerComposeFilename = dockerComposeFilename
        self.dockerComposeProjectName = dockerComposeProjectName
        self.threadMap = threadMap
        self.threadFinishedMap = threadFinishedMap

    def run(self):
        if "dependOn" in self.eventObject:
            for dependOn in self.eventObject["dependOn"]:
                if not self.threadFinishedMap[dependOn]:
                    while not self.threadFinishedMap[dependOn]:
                        pass

        if "seconds" in self.eventObject:
            print "sleep for " + str(self.eventObject["seconds"]) + " seconds"
            time.sleep(int(self.eventObject["seconds"]))

        if "command" in self.eventObject:
            print "execute command: " + self.eventObject["command"]
            exitCode = call(self.eventObject["command"], shell=True)
            if exitCode != 0:
                print "command exited with exit code " + str(exitCode) + ". Abort."
                return exitCode

        if "commands" in self.eventObject:
            for command in self.eventObject["commands"]:
                print "execute command: " + command
                exitCode = call(command, shell=True)
                if exitCode != 0:
                    print "command exited with exit code " + str(exitCode) + ". Abort."
                    return exitCode

        # TODO support docker exec OPTIONS, see https://docs.docker.com/engine/reference/commandline/exec/
        if "docker_exec" in self.eventObject:
            docker_exec = self.eventObject["docker_exec"]
            container_id = check_output("docker ps -aqf name=" + docker_exec["container"], shell=True).strip()
            for command in docker_exec["commands"]:
                full_command = "docker exec " + container_id + command
                print "run: docker exec " + container_id + command
                exitCode = call("docker exec " + container_id + command, shell=True)
                if exitCode != 0:
                    print "command exited with exit code " + str(exitCode) + ". Abort."
                    return exitCode

        if "do" in self.eventObject:
            doObject = self.eventObject["do"]
            for action in doObject:
                exitCode = executeAction(action, doObject[action], self.dockerComposeFilename, self.dockerComposeProjectName)
                if exitCode != 0:
                    print action + " exited with exit code " + str(exitCode)
        self.threadFinishedMap[self.eventKey] = True
