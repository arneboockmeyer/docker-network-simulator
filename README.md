# Docker Network Simulator

## Requirements

* Python 2.7 installed
* PyYaml installed (see: [documentation](http://pyyaml.org/wiki/PyYAML))
* Docker with Docker-compose installed

## Example-Run:

```
python main.py examples/example-containers.yaml
```

## YAML-File

The YAML-File needs two keys, `setup` and `events` on the base level.
```yaml
setup:
    # docker-compose setup
events:
    # processed by event engine
```

The setup part will be piped directly to docker-compose.
This means, the whole part of container setup is managed by docker-compose.
You can use each version of the docker-compose-file and all supported features.

The events part is processed with this tool.
The second level of this part is a key-value map of all events:
```yaml
setup:
    docker-compose setup
events:
    event1:
        # event
    event2:
        # event
```

### Events
Each event can be directly identified with the key and has the following structure:
```yaml
event1:
    dependOn: <list-of-events>
    seconds: <amount-of-seconds>
    commands:
      - command1
      - command2
      - ....
    docker_exec:
      container: <docker node name from setup part>
      commands: <commands to be executed in docker exec>
    do:
        <map of actions>
```

The first three keys describes when the `do`-block should be executed.
The order of these conditions is as shown above.
This means for example that after the events this event1 dependsOn have returned, the program waited a few seconds and the commands have succesfully been executed the do-part of this event will be executed.

#### dependOn
`dependOn` takes a list of other events (identified with their keys).
This means the execution of the actions waits for the other events until they have executed their `do`-block.

Example:
```yaml
dependOn: ["evt2", "evt3"]
```
This means, the execution waits until the events `evt2` and `evt3` have finished.

#### seconds
Delays the execution of the `do`-block for a few seconds.
The value has to be a number (in seconds).

Example:
```yaml
seconds: 5
```
This means the execution waits 5 seconds.

#### commands
It can execute any list of commands and if this command returns `1`, the `do`-block will be executed.

Example:
```yaml
commands:
  - ping -c 1 192.168.1.2
  - ls
```
This would test if the computer with the IP-address `192.168.1.2` is reachable and execute the `do`-block (if there is a connection) once the command returned `1`. Afterwards it executes ls and executes the `do`-block if ls succeeds.

#### command (outdated)

It can execute any command and if this command returns `1`, the `do`-block will be executed.

Example:
```yaml
command: ping -c 1 192.168.1.2
```

This would test if the computer with the IP-adress `192.168.1.2` is reachable and execute the `do`-block (if there is a connection) once the command returned `1`.

#### docker_exec
`docker_exec` takes the node name specified in the setup part and executes the `command`-collection with `docker exec`

Example:
```yaml
docker_exec:
  container: node1
  commands:
    - ping -c 1 192.168.1.2
    - ls
```


#### do
The `do`-block will be executed when all conditions (see above) were processed.
Its a map from the key of an action to the values of these actions.

Example:
```yaml
do:
    startTimer: ["T1"]
    join: ["Node1", "Node2"]
```

This means after all conditions are processed the script will start a timer with the name `T1` and join the nodes `Node1` and `Node2`.

Be careful: The actions specified in the do-section will not necessarily be executed in the given order.

### Actions

This tools supports 12 actions so far.

#### startTimer

This actions takes a list of keys (the identifiers of the actions).
It stores the current milliseconds value to a dictionary with these keys.
Use `printTimer` and `stopTimer` to print the duration to the console.

Example:
```yaml
startTimer: ["T1", "T2", "T3"]
```

#### printTimer

This actions takes a list of timer-keys.
Prints the current value of the timer (the difference of the current time to the start time).

Example:
```yaml
printTimer: ["T1"]
```

#### stopTimer

This actions also takes a list of timer-keys.
It prints the current value of the timer and removes the key from the dictionary.

Example:
```yaml
stopTimer: ["T1"]
```

#### join

This actions takes up to three keys: `container`, `internal` and `mode`.
The value `container` are the identifiers of the containers, specified in the setup parts.
The action will create a new network and add these containers to the network.
The sorted list of the containers is the key of the network (not the name).

The value of `internal` can be `True` or `False`.
It maps to the [internal flag](https://docs.docker.com/engine/reference/commandline/network_create/#network-internal-mode) of docker.

The `mode` can be any of `row`, `ring` or `cluster`.
If the `mode` is `cluster` one network with all containers will be created.
If the `mode` is `row` a separate network will be created for each pair of containers which are next to each other in the `container` list.
If the `mode` is `ring` it also connects the ends to each other.

`internal` and `mode` are optional. The default values are `False` for `internal` and `cluster` for `mode`.

Example:
```yaml
join:
    container: ["Node1", "Node2", "Node3"]
    internal: True
    mode: "ring"
```

This will create the networks `Node1 - Node2`, `Node2 - Node3` and `Node3 - Node1`.

#### cut

To cut networks which were created with `join` use the simple `cut` action.
It takes a list of container-ids, which represents the network.

Example:
Lets assume you joined your nodes with the following action:
```yaml
join:
    container: ["Node1", "Node2", "Node3"]
    internal: True
    mode: "ring"
```

You can cut all three networks by calling the following action for example:
```yaml
cut:
    container: ["Node1", "Node3"]
```
It deletes the network with `Node1` and `Node3` (the order doesn't matter).

#### startContainer, stopContainer and restartContainer

These actions can start, stop and restart single containers.
All of them take a list of containers and execute the docker-compose command to execute the action.

Example:
```yaml
startContainer: ["Node1"]
stopContainer: ["Node2"]
restartContainer: ["Node3"]
```

This example starts `Node1`, stops `Node2` and restarts `Node3`.

#### delay, duplicate, corrupt and loss
These actions use the linux network emulator `netem`.
Make sure that your container support this network emulator when using this command.
Have a look at the [documentation](http://man7.org/linux/man-pages/man8/tc-netem.8.html) for details.

Example:
```yaml
delay:
    network: ["Node1", "Node2"]
    time: "100ms"
    jitter: "20ms"
    correlation: "25%"
    distribution: "normal"
duplicate:
    network: ["Node1", "Node2"]
    percent: 10
    correlation: "25%"
corrupt:
    network: ["Node1", "Node2"]
    percent: 10
    correlation: "25%"
loss:
    network: ["Node1", "Node2"]
    percent: 10
    correlation: "25%"
```

The `network`-key describes the effected network.
Be careful: If you add a delay (or a duplicate, corrupt or loss effect) to a network the delay will be added to each container in that network.
This means the real delay is as twice as much as given (outgoing from one container ingoing in the other one).
For all other fields have a look in the [documentation](http://man7.org/linux/man-pages/man8/tc-netem.8.html).

Please note: You also need to add network capabilities to your containers:
```yaml
cap_add:
- NET_ADMIN
```

## Networking with the Docker Network Simulator

We recommend to create all networks in a setup with the `join` action and not with docker-compose itself.
Otherwise you can not cut them with the `cut` actions.
If you don't need this you can also use the docker-compose way.

If you like to have an isolated environment, don't forget to add the `internal`-flag when joining a few nodes and add the field `network_mode: "none"` to all containers.


## Data-Exchange between containers

To exchange data between two containers without using a network between them we used a shared directory in the past.
You can add a volume to each container and use files in the volume to exchange data.
See the docker-compose documentation for [volumes](https://docs.docker.com/compose/compose-file/#volumes) for more details.

## Examples

Have look at the examples folder in this repository to see some examples.

## Implementation

The setup part of the input-yaml will be written to a new file.
This file will be used by docker-compose (see `docker-compose up`).
After executing all events the docker compose environment will be stopped with `docker-compose down` and the docker-compose file will be deleted.
All created networks will be deleted as well.
After a full run of this tool there shouldn't be any artifacts left.

Each event will be executed in a single thread. This threading causes sometimes some weird issues and can effect the precision of the timers.

The `main.py`-file starts the docker-compose environment and creates the threads.
The `eventWorker.py`-file executes a single event.
The `executeAction.py`-file distributes the actions to their implementations, which are located in the `actions`-folder.
