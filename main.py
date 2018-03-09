"""Main module of the docker network simulator"""

import time
import argparse
import yaml
import hashlib
import os
import datetime
from subprocess import call
from threading import Thread
from threading import Timer
import collections
from eventWorker import eventWorker
from actions.networkActions import deleteAllNetworks

parser = argparse.ArgumentParser(prog='main.py', usage='%(prog)s configurationFile')
parser.add_argument('configurationFile', nargs='?', help='Specify the configuration file')

args = parser.parse_args()

configFile = args.configurationFile

# Read config file
yamlString = ""
with open(configFile, 'r') as fileContent:
    yamlString = fileContent.read()

# Parse YAML
yamlConfig = yaml.load(yamlString)

# Write Docker Compose File
now = datetime.datetime.now()
dateHash = hashlib.sha256(str(now)).hexdigest()
dockerComposeFilename = str(dateHash)+".yaml"
dockerComposeProjectName = "networksimulator"
with open(dockerComposeFilename, 'w+') as filePointer:
    filePointer.write(yaml.dump(yamlConfig['setup']))

# Start Docker Compose
call(["docker-compose", "-p", dockerComposeProjectName, "-f", dockerComposeFilename, "up", "-d"])


# Insert event management here:
print "##### ##### ##### ##### ##### #####\n##### ### EventManagement ##### ###\n##### ##### ##### ##### ##### #####"
events = yamlConfig['events']

threads = {}
threadsFinished = {}

# Create all workers
for event in events:
    threadsFinished[event] = False
    threads[event] = eventWorker(event, events[event], dockerComposeFilename, dockerComposeProjectName, threads, threadsFinished)

# start all threads
for thread in threads:
    threads[thread].start()

# Wait for all before finishing
for thread in threads:
    threads[thread].join()

print "Finished..."
print "##### ##### ##### ##### ##### #####\n##### ### EventManagement ##### ###\n##### ##### ##### ##### ##### #####"
# Stop docker compose and delete file
call(["docker-compose", "-p", dockerComposeProjectName, "-f", dockerComposeFilename, "down"])
os.remove(dockerComposeFilename)
deleteAllNetworks()
