# Import the modules
from controller import Supervisor
import paho.mqtt.client as mqtt
import json
from collections import deque

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker (WeBots)")

def on_message(client, userdata, message):
    global target
    global tarX
    global tarY
    global other_bots_remote
    global location_bot1_remote
    global location_bot2_remote
    global location_bot3_remote
    global location_bot4_remote

    if message.topic == "noodstop":
       global noodstop
       noodstop = True
    
    if message.topic == bot_name + "/target":
        message = str(message.payload.decode("utf-8"))
        tarX = int(message[0])
        tarY = int(message[2])
        target = (tarX, tarY)


    elif message.topic[0:4] != bot_name:
        if message.topic[4:7] == "/lo":
            if message.topic[0:4] == "bot1":
                dec_msg = (message.payload.decode("utf-8"))
                location_bot1_remote = (int(dec_msg[0]),int(dec_msg[2]))
            elif message.topic[0:4] == "bot2":
                dec_msg = (message.payload.decode("utf-8"))
                location_bot2_remote = (int(dec_msg[0]),int(dec_msg[2]))
            elif message.topic[0:4] == "bot3":
                dec_msg = (message.payload.decode("utf-8"))
                location_bot3_remote = (int(dec_msg[0]),int(dec_msg[2]))
            elif message.topic[0:4] == "bot4":
                dec_msg = (message.payload.decode("utf-8"))
                location_bot4_remote = (int(dec_msg[0]),int(dec_msg[2]))



# Help function to add neighbors for the location in adjacency list
def add_adjacent(adjacency_list, location, adjacent):
    adjacency_list[location].add(adjacent)
    adjacency_list[adjacent].add(location)

def update_graph(adjacency_list, obstacles, old_location, new_location):
    # Check if moving one step to the right is a valid move
    if (old_location[0] + 1 != new_location[0] and
        old_location[0] + 1 <= 9 and
            (old_location[0] + 1, old_location[1]) not in obstacles):
        # Update the adjacency list by adding the new location as an adjacent node to the old location
        add_adjacent(adjacency_list, old_location,
                     (old_location[0] + 1, old_location[1]))

    # Check if moving one step to the left is a valid move
    if (old_location[0] - 1 != new_location[0] and
        old_location[0] - 1 >= 0 and
            (old_location[0] - 1, old_location[1]) not in obstacles):
        # Update the adjacency list by adding the new location as an adjacent node to the old location
        add_adjacent(adjacency_list, old_location,
                     (old_location[0] - 1, old_location[1]))

    # Check if moving one step up is a valid move
    if (old_location[1] + 1 != new_location[1] and
        old_location[1] + 1 <= 9 and
            (old_location[0], old_location[1] + 1) not in obstacles):
        # Update the adjacency list by adding the new location as an adjacent node to the old location
        add_adjacent(adjacency_list, old_location,
                     (old_location[0], old_location[1] + 1))

    # Check if moving one step down is a valid move
    if (old_location[1] - 1 != new_location[1] and
        old_location[1] - 1 >= 0 and
            (old_location[0], old_location[1] - 1) not in obstacles):
        # Update the adjacency list by adding the new location as an adjacent node to the old location
        add_adjacent(adjacency_list, old_location,
                     (old_location[0], old_location[1] - 1))

    # Remove the new location from the neighbors of new's neighbors
    for adjacent_node in adjacency_list[new_location]:
        if new_location in adjacency_list[adjacent_node]:
            adjacency_list[adjacent_node].remove(new_location)

    # Clear the adjacency list of the new location
    adjacency_list[new_location].clear()

    return adjacency_list


# Add obstacle and send updated obs list to server
def add_obstacle(adjacency_list, obstacle):
    local_obs_list.append(obstacle)
    # Reset adjacents
    for adjacent_node in adjacency_list[obstacle]:
        if obstacle in adjacency_list[adjacent_node]:
            adjacency_list[adjacent_node].remove(obstacle)
    adjacency_list[obstacle].clear()

    # Publish the obstacle list for every bot 
    client.publish(bot_name + "/obstacle", json.dumps(local_obs_list))
    
def create_graph(adjacency_list, obstacles_units):
    # Iterate over each grid cell in the 10x10 grid
    for i in range(10):
        for j in range(10):
            # Set to store the adjoined cells of the current cell
            adjoined = set()

            # Check if the current cell is not an obstacle
            if (i, j) not in obstacles_units:
                # Check and add the left adjacent cell if it is not an obstacle
                if i > 0 and (i - 1, j) not in obstacles_units:
                    adjoined.add((i - 1, j))

                # Check and add the right adjacent cell if it is not an obstacle
                if i < 9 and (i + 1, j) not in obstacles_units:
                    adjoined.add((i + 1, j))

                # Check and add the top adjacent cell if it is not an obstacle
                if j > 0 and (i, j - 1) not in obstacles_units:
                    adjoined.add((i, j - 1))

                # Check and add the bottom adjacent cell if it is not an obstacle
                if j < 9 and (i, j + 1) not in obstacles_units:
                    adjoined.add((i, j + 1))

            # Update the adjacency list entry for the current cell
            adjacency_list[(i, j)] = adjoined

    # Return the updated adjacency list representing the graph
    return adjacency_list

def gen_traversal(s):
    q = deque()
    q.append(s)

    # Initialize a dictionary to track visited nodes and mark the starting node as visited
    visited = {node: False for node in graph}
    visited[s] = True

    # Initialize a dictionary to track the previous node for each node in the traversal path
    prev = {node: None for node in graph}

    # Perform breadth-first search traversal
    while q:
        # Dequeue the next node from the queue
        node = q.popleft()

        # Get the neighbors of the current node
        adjoined = graph[node]

        # Iterate over the neighbors and process unvisited neighbors
        for next in adjoined:
            if not visited[next]:
                # Enqueue the unvisited neighbor
                q.append(next)

                # Mark the neighbor as visited
                visited[next] = True

                # Update the previous node mapping
                prev[next] = node

    # Return the dictionary mapping each node to its previous node in the traversal path
    return prev

def gen_path(s, e, prev):
    # Initialize an empty list to store the reconstructed path
    path = []

    # Set the current node to the end node
    p = e

    # Reconstruct the path by following the previous node pointers in the prev dictionary
    while p:
        # Append the current node to the path
        path.append(p)

        # Update the current node to its previous node
        p = prev[p]

    # Reverse the path to get it from start node to end node order
    path.reverse()

    # Return the reconstructed path from s to e, excluding the start node if it exists
    return path[1:] if path[0] == s else []

def breadth_first_search(s, e):
    prev = gen_traversal(s)
    return gen_path(s, e, prev)

def show_led(current, next):
    # Show bot direction on bot and hardware LED
    if next[0] > current[0]:
        leds[1].set(1)
        client.publish(bot_name + "/direction", "E")
    elif next[0] < current[0]:
        leds[3].set(1)
        client.publish(bot_name + "/direction", "W")
    elif next[1] < current[1]:
        leds[0].set(1)
        client.publish(bot_name + "/direction", "N")
    elif next[1] > current[1]:
        leds[2].set(1)
        client.publish(bot_name + "/direction", "S")
    

# Instanciate the robot
robot = Supervisor()
supervisorNode = robot.getSelf()

# Get bot values
bot_name = supervisorNode.getField("name").getSFString()
target = supervisorNode.getField("target").getSFVec2f()
trans = supervisorNode.getField("translation")

# Connect to MQTT Broker
broker_address="localhost"
client = mqtt.Client(transport="websockets") 
client.connect(broker_address, 1884)

# Subscribe to all topics
client.subscribe(bot_name + "/target")
client.subscribe("noodstop")
client.on_connect = on_connect
client.on_message = on_message
client.loop_start()

# Variable to know that we are in first pos
initPos = True

# Instanciate object for emergency stop
noodstop = False

# Get worlds time set
timestep = int(robot.getBasicTimeStep())
duration = (1000 // timestep) * timestep

# Instanciate the child devices on the robot
leds = [robot.getDevice("l_n"), robot.getDevice("l_e"), robot.getDevice("l_s"), robot.getDevice("l_w")]
sensors= [robot.getDevice("s_n"), robot.getDevice("s_e"), robot.getDevice("s_s"), robot.getDevice("s_w")]

# Enable the sensors
for sensor in sensors:
    sensor.enable(1)

location_bot1 = (0, 0)
location_bot2 = (9, 0)
location_bot3 = (9, 9)
location_bot4 = (0, 9)

location_bot1_remote = (0, 0)
location_bot2_remote = (9, 0)
location_bot3_remote = (9, 9)
location_bot4_remote = (0, 9)

other_bots = [
    location_bot1,
    location_bot2,
    location_bot3,
    location_bot4,
]

other_bots_remote = [
    location_bot1_remote,
    location_bot2_remote,
    location_bot3_remote,
    location_bot4_remote,
]

location_topics = [
    "bot1/location",
    "bot2/location",
    "bot3/location",
    "bot4/location",
]

for topic in location_topics:
    client.subscribe(topic)

# Remove own position from the other_bots list
this_unit_pos = supervisorNode.getPosition()

# Remove unit itself from other_units
other_bots.remove((round(10 * this_unit_pos[0]), round(-10 * this_unit_pos[1])))
other_bots_remote.remove((round(10 * this_unit_pos[0]), round(-10 * this_unit_pos[1])))

# Instanciate the local and remote obstacle list
local_obs_list = []

# Instanciate the graph
graph = create_graph({}, other_bots)

# While loop for bot
while robot.step(duration) != -1:
    # Turn off all leds
    for led in leds:
        led.set(0)

    # Handle emergency stop
    if noodstop:
        client.publish(bot_name + "/direction", "X")
        for led in leds:
            led.set(0)
        break

    # Get current position and target
    bot_position = supervisorNode.getPosition()

    # Get sensor values
    n_sens_val = sensors[0].getValue()
    e_sens_val = sensors[1].getValue()
    s_sens_val = sensors[2].getValue()
    w_sens_val = sensors[3].getValue()

    # Update graph location based on other nodes
    if bot_name == "bot1":
        other_bots_remote[0] = location_bot2_remote
        other_bots_remote[1] = location_bot3_remote
        other_bots_remote[2] = location_bot4_remote
    elif bot_name == "bot2":
        other_bots_remote[0] = location_bot1_remote
        other_bots_remote[1] = location_bot3_remote
        other_bots_remote[2] = location_bot4_remote
    elif bot_name == "bot3":
        other_bots_remote[0] = location_bot1_remote
        other_bots_remote[1] = location_bot2_remote
        other_bots_remote[2] = location_bot4_remote
    elif bot_name == "bot4":
        other_bots_remote[0] = location_bot1_remote
        other_bots_remote[1] = location_bot2_remote
        other_bots_remote[2] = location_bot3_remote

    if location_bot1 != location_bot1_remote:
        update_graph(graph, obstacles+other_bots_remote, location_bot1, location_bot1_remote)
        location_bot1 = location_bot1_remote
    if location_bot2 != location_bot2_remote:
        update_graph(graph, obstacles+other_bots_remote, location_bot2, location_bot2_remote)
        location_bot2 = location_bot2_remote
    if location_bot3 != location_bot3_remote:
        update_graph(graph, obstacles+other_bots_remote, location_bot3, location_bot3_remote)
        location_bot3 = location_bot3_remote
    if location_bot4 != location_bot4_remote:
        update_graph(graph, obstacles+other_bots_remote, location_bot4, location_bot4_remote)
        location_bot4 = location_bot4_remote

    # Get current position and target in integer coords
    cur_pos = (round(10 * bot_position[0]),   
               round(-10 * bot_position[1]))
        
    target = (round(target[0]),
              round(target[1]))
    
    # Only send current position if it has changed
    if initPos:
        client.publish(bot_name + "/location", "{};{}".format(cur_pos[0], cur_pos[1]))
        initPos = False
        oldPos = cur_pos

    if oldPos != cur_pos:
        client.publish(bot_name + "/location", "{};{}".format(cur_pos[0], cur_pos[1]))
        oldPos = cur_pos

    # Get obstacle coordinates
    obstacle = ()
    if n_sens_val < 1000 and cur_pos[1] != 0:
        obstacle = (cur_pos[0], cur_pos[1] - 1)
        if obstacle not in local_obs_list:
            add_obstacle(graph, obstacle)
    if e_sens_val < 1000 and cur_pos[0] != 9:
        obstacle = (cur_pos[0] + 1, cur_pos[1])
        if obstacle not in local_obs_list:
            add_obstacle(graph, obstacle)
    if s_sens_val < 1000 and cur_pos[1] != 9:
        obstacle = (cur_pos[0], cur_pos[1] + 1)
        if obstacle not in local_obs_list:
            add_obstacle(graph, obstacle)
    if w_sens_val < 1000 and cur_pos[0] != 0:
        obstacle = (cur_pos[0] - 1, cur_pos[1])
        if obstacle not in local_obs_list:
            add_obstacle(graph, obstacle)

    obstacles = ["0","0","0","0"]

    for i in range(len(sensors)):
        if sensors[i].getValue() < 1000:
            obstacles[i] = "1"
    
    client.publish(bot_name + "/obstaclebin", ("".join(obstacles)))

    # Calculate path if possible
    if target != cur_pos:
        path = breadth_first_search(cur_pos, target)
        if path:
            # path exists
            show_led(cur_pos, path[0])
            trans.setSFVec3f(
                [path[0][0]/10, -1 * path[0][1]/10, 0.05])
        else:
            print("Er is geen path gevonden voor bot: " + bot_name)
    else:
        client.publish(bot_name + "/direction", "X")