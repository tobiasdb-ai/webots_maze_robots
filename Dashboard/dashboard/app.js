const host = 'ws://localhost:1884';
const sendButton = document.getElementById("sendButton");
sendButton.addEventListener("click", sendCommand);
let completedTasks = []; 

const options = {
    keepalive: 50,
    protocolVersion: 4,
    clean: true,
    reconnectPeriod: 2000,
    connectTimeout: 50000,
};

let queue = {
    bot1: [],
    bot2: [],
    bot3: [],
    bot4: []
  };

const client = mqtt.connect(host, options);

const subscriptions = ["bot1/#", "bot2/#", "bot3/#", "bot4/#"]

//Connection lukt
client.on('connect', () => {
    console.log('Connected to the broker');
    subscriptions.forEach(topic => client.subscribe(topic));
});

let botData = {
    bot1: {
        location: { X: -1, Y: -1 },
        obstacles: "0000"
    },
    bot2: {
        location: { X: -1, Y: -1 },
        obstacles: "0000"
    },
    bot3: {
        location: { X: -1, Y: -1 },
        obstacles: "0000"
    },
    bot4: {
        location: { X: -1, Y: -1 },
        obstacles: "0000"
    }
};

client.on('message', (topic, message, packet) => {
    console.log("Message received " + message + " on topic " + topic);

    const botName = topic.split('/')[0];
    const messageType = topic.split('/')[1];

        if (messageType === 'location') {
            const [x, y] = message.toString().split(';');
            botData[botName].location.X = parseInt(x);
            botData[botName].location.Y = parseInt(y);
            switch (botName) {
                case 'bot1':
                    robot1.clearRect(20 * previousX1, 20 * previousY1, 20, 20);
                    drawRobot1(botData[botName].location.X + 1, botData[botName].location.Y + 1);
                    updateBotCoordinates('bot1', botData[botName].location.X, botData[botName].location.Y);
                    break;
                case 'bot2':
                    robot2.clearRect(20 * previousX2, 20 * previousY2, 20, 20);
                    drawRobot2(botData[botName].location.X + 1, botData[botName].location.Y + 1);
                    updateBotCoordinates('bot2', botData[botName].location.X, botData[botName].location.Y);
                    break;
                case 'bot3':
                    robot3.clearRect(20 * previousX3, 20 * previousY3, 20, 20);
                    drawRobot3(botData[botName].location.X + 1, botData[botName].location.Y + 1);
                    updateBotCoordinates('bot3', botData[botName].location.X, botData[botName].location.Y);
                    break;
                case 'bot4':
                    robot4.clearRect(20 * previousX4, 20 * previousY4, 20, 20);
                    drawRobot4(botData[botName].location.X + 1, botData[botName].location.Y + 1);
                    updateBotCoordinates('bot4', botData[botName].location.X, botData[botName].location.Y);
                    break;
                default:
                    break;
            }

        } else if (messageType === 'obstaclebin') {
            

            botData[botName].obstacles = message.toString();
            let obstacles = botData[botName].obstacles;
            let obsNorth = obstacles.charAt(0);
            let obsEast = obstacles.charAt(1);
            let obsSouth = obstacles.charAt(2);
            let obsWest = obstacles.charAt(3);
            if (obsNorth == '1'){
                obstacleList.push({ X: botData[botName].location.X, Y: botData[botName].location.Y - 1 });
                drawObstacle(botData[botName].location.X + 1, botData[botName].location.Y - 1 + 1);
            }
            if (obsEast == '1'){
                obstacleList.push({ X: botData[botName].location.X + 1, Y: botData[botName].location.Y});
                drawObstacle(botData[botName].location.X + 1 + 1, botData[botName].location.Y + 1);

            }
            if (obsSouth == '1'){
                obstacleList.push({ X: botData[botName].location.X, Y: botData[botName].location.Y + 1});
                drawObstacle(botData[botName].location.X + 1, botData[botName].location.Y + 1 + 1);

            }
            if (obsWest == '1'){
                obstacleList.push({ X: botData[botName].location.X - 1, Y: botData[botName].location.Y});
                drawObstacle(botData[botName].location.X + 1 - 1, botData[botName].location.Y + 1);

            }
        }
        console.log(obstacleList);
        

});

//Connection lukt niet
client.on('error', (err) => {
    console.log('Connection failed error: ', err);
    client.end();
});

function noodstop() {
    client.publish("noodstop", "Y");
    client.publish("bot1/direction", "X");
    client.publish("bot2/direction", "X");
    client.publish("bot3/direction", "X");
    client.publish("bot4/direction", "X");
}
function sendCommand() {
    const unit = document.getElementById("unit").value;
    const target = document.getElementById("target").value;

    const originX = botData[unit].location.X;
    const originY = botData[unit].location.Y;

    const task = {
        originX: originX,
        originY: originY,
        targetX: parseInt(target.split(";")[0]),
        targetY: parseInt(target.split(";")[1])
    };

    queue[unit].push(task);
    console.log(queue);

    document.getElementById("target").value = "";
    updateQueueDisplay();
}

function updateBotCoordinates(botName, x, y) {
    const botCoordinatesSpan = document.getElementById(botName + "Coordinates");
    botCoordinatesSpan.textContent = " (" + x + ", " + y + ")";
}

function updateBotCoordinates(botName, x, y) {
    const botCoordinatesSpan = document.getElementById(botName + "Coordinates");
    botCoordinatesSpan.textContent = " (" + x + ", " + y + ")";
}

function sendTarget(unit, x, y) {
    client.publish(unit + "/target", x + ";" + y);
}

  function addToQueue() {
    const originInput = document.getElementById("origin");
    const targetInput = document.getElementById("target2");
    const unitInput = document.getElementById("unit");

    const origin = originInput.value.split(";").map(Number);
    const target = targetInput.value.split(";").map(Number);
    const unit = unitInput.value;

    const task = {
        originX: origin[0],
        originY: origin[1],
        targetX: target[0],
        targetY: target[1],
        completed: false // Add the completed property and set it to false
    };

    if (isNaN(task.originX) || isNaN(task.originY) || isNaN(task.targetX) || isNaN(task.targetY)) {
        alert("Invalid input!");
        return;
    }

    queue[unit].push(task);
    originInput.value = "";
    targetInput.value = "";

}


function moveRobots() {
    for (let unit in queue) {
      // Check if the robot has any tasks in the queue
      if (queue[unit].length > 0) {
        let task = queue[unit][0]; // Get the first task in the queue
  
        // Check if the robot is already at the pickup location
        if (
          botData[unit].location.X === task.originX &&
          botData[unit].location.Y === task.originY
        ) {
          // Check if the robot has already picked up the item
          if (!botData[unit].hasItem) {
            // Robot is at the pickup location and hasn't picked up the item yet
            // You can add code here to simulate picking up the item or any other desired behavior
            botData[unit].hasItem = true;
            // For example, you can log a message indicating the item pickup
            console.log(unit + " picked up the item.");
          } else {
            // Robot has the item, move it to the delivery location
            sendTarget(unit, task.targetX, task.targetY);
          }
        } else if (
          botData[unit].location.X === task.targetX &&
          botData[unit].location.Y === task.targetY &&
          botData[unit].hasItem
        ) {
          // Robot has reached the delivery location and has the item
          console.log(unit + " delivered the item.");
  
          queue[unit].shift(); // Remove the completed task from the queue
          // Reset the hasItem flag for the robot
          botData[unit].hasItem = false;
  
          // Mark the task as completed
          task.completed = true;
          task.completedBy = unit;
  
          // Move the completed task to the completedTasks array
          completedTasks.push(task);
  
          // Update the completed tasks container in the HTML
          updateCompletedTasks();
        } else {
          // Robot is not yet at the pickup or delivery location, move it towards the location
          if (!botData[unit].hasItem) {
            sendTarget(unit, task.originX, task.originY);
          } else {
            sendTarget(unit, task.targetX, task.targetY);
          }
        }
      }
    }
}

  function updateCompletedTasks() {
    // Get the completed tasks container element
    const completedContainer = document.getElementById("completedContainer");

    // Clear the container
    completedContainer.innerHTML = "<h2>Completed Tasks:</h2>";

    // Loop through the completed tasks and add them to the container
    for (let i = 0; i < completedTasks.length; i++) {
        const task = completedTasks[i];
        const taskElement = document.createElement("div");
        taskElement.textContent = `Task: ${task.originX},${task.originY} -> ${task.targetX},${task.targetY} (Completed by: ${task.completedBy})`;
        completedContainer.appendChild(taskElement);
    }
}

let obstacleList = [];

function updateQueueDisplay() {
    const queueContainer = document.getElementById("queueContainer");
    queueContainer.innerHTML = "";
  
    Object.entries(queue).forEach(([unit, tasks]) => {
        tasks.forEach((task, index) => {
        const pickupElement = document.createElement("div");
        const taskStatus = task.completed ? "Completed" : (index === 0 ? "Ongoing" : "Pending");
        pickupElement.textContent = `${unit} - Pickup: (${task.originX},${task.originY}) - Target: (${task.targetX},${task.targetY}) `;
        queueContainer.appendChild(pickupElement);
        });
    });
}

const canvas = document.getElementById("theCanvas");
const border = canvas.getContext("2d");
const obstacles = canvas.getContext("2d");
const robot1 = canvas.getContext("2d");
const robot2 = canvas.getContext("2d");
const robot3 = canvas.getContext("2d");
const robot4 = canvas.getContext("2d");

canvas.width = 240;
canvas.height = 240;

CanvasRenderingContext2D.prototype.drawBlock = function(x, y) {
  this.fillRect(20 * x, 20 * y, 20, 20)
};

let previousX1 = -1;
let previousY1 = -1;
let previousX2 = -1;
let previousY2 = -1;
let previousX3 = -1;
let previousY3 = -1;
let previousX4 = -1;
let previousY4 = -1;

function clearCanvas() {
  robot1.clearRect(20 * previousX1, 20 * previousY1, 20, 20);
  robot2.clearRect(20 * previousX2, 20 * previousY2, 20, 20);
  robot3.clearRect(20 * previousX3, 20 * previousY3, 20, 20);
  robot4.clearRect(20 * previousX4, 20 * previousY4, 20, 20);
}

function drawRobot1(x, y) {
    console.log(x,y);
    robot1.fillStyle = "red";
    robot1.drawBlock(x, y);
    previousX1 = x;
    previousY1 = y;
}

function drawRobot2(x, y) {
    robot2.fillStyle = "green";
    robot2.drawBlock(x, y);
    previousX2 = x;
    previousY2 = y;
}

function drawRobot3(x, y) {
    robot3.fillStyle = "blue";
    robot3.drawBlock(x, y);
    previousX3 = x;
    previousY3 = y;
}

function drawRobot4(x, y) {
    console.log("AYO");
    robot4.fillStyle = "yellow";
    robot4.drawBlock(x, y);
    previousX4 = x;
    previousY4 = y;
}

function drawObstacle(x, y) {
    // Check if the current obstacle being drawn is a robot
    if (x -1 === botData.bot1.location.X && y -1 === botData.bot1.location.Y){
    
    }
    else if (x -1 === botData.bot2.location.X && y -1 === botData.bot2.location.Y){
    
    }
    else if (x -1 === botData.bot3.location.X && y -1 === botData.bot3.location.Y){
    
    }
    else if (x -1 === botData.bot4.location.X && y -1 === botData.bot4.location.Y){

    }
    else {
        // Draw the robot
        obstacles.fillStyle = "darkred";
        obstacles.drawBlock(x, y);
    }
}

setInterval(moveRobots, 1000);
updateCompletedTasks();