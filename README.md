# Transceiver-5298 #
Networking code written for the FIRST Robotics competition to allow the main robot processor to communicate with a Raspberry Pi coprocessor.

## Overview ##
Image processing is used in the competition to line up with & grab targets.
Usually, this code is run on a coprocessor and fed back to the main controller.

Most teams do not attempt Image processing due to the learning curve of OpenCV and Networking/Remote Procedure Calls.
So, here's my stab at it.

The main processor acts as a Java client, and the Raspberry Pi acts as a Python server.

### Client-side
The main processor uses a Java framework for the competition, which is (mostly) single-threaded.
It's great for High-School students to quickly learn & use, but is sort of painful to work with for more advanced applications.
So we have to work with what we have.

Our solution was to spin off a thread to monitor sockets & communicate with the main framework via ConcurrentQueues.
The Java socket client sends commands to the Python server via TCP, since the commands must be received.

### Server-side
Because we're not limited on the server-side, we run OpenCV & Python on a Raspberry Pi.
We use an asynchronous paradigm (asyncio) to read from the socket, and pass it to worker threads.
Commands from the Java client are used to pause & resume the worker threads.

The Python server returns a stream of positional data via UDP.

## To Run
Upload the code in `Python/` to the Raspberry Pi using SFTP and run it with:
`python3 Python/server.py`

Then clone the Java code onto your host machine. Compile the code by with the following commands:
`cd Java/`
`javac -cp . First.java`

Now run the client code:
`java First`
