## To Run  ##

Upload the code in `Python/` to the Raspberry Pi using SFTP and run it with:
`python3 Python/server.py`

Then clone the Java code onto your host machine. Compile the code by with the following commands:
`cd Java/`
`javac -cp . First.java`

Now run the client code:
`java First`