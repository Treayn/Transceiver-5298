import java.io.*;
import java.net.*;
import java.util.concurrent.*;

//package FRC;

public class Transceiver /*extends Subsystem*/ {
    // All queues hold strings, class methods are used to convert from strings to other types as needed.
    // Outbound queue is used to send commands to the Raspberry Pi.
    private ConcurrentLinkedQueue<String> outboundQueue;

    // Inbound queues receive data from the Raspberry Pi, which get sorted into different queues.
    private ConcurrentHashMap<String, ConcurrentLinkedQueue<String>> inboundQueues;

    // Threads that open sockets to talk to the Raspberry Pi.
    Thread transmitter, receiver;

    // the Transmitter class takes strings off the queue and sends them to the Raspberry Pi.
    static class Transmitter implements Runnable {
        private ConcurrentLinkedQueue<String> queue;
        private Socket socket;

        private DataOutputStream output;
        private boolean shouldStop;

        Transmitter(ConcurrentLinkedQueue<String> queue) {
            System.out.println("Creating Transmitter...");
            try {
                socket = new Socket("192.168.1.197", 5805);
                System.out.println("Transmitter Connected.");
                output = new DataOutputStream(socket.getOutputStream());
            } catch(Exception ex) {
                ex.printStackTrace();
            }

            this.queue = queue;
            shouldStop = false;
        }

        public void run() {
            String data;
            System.out.println("Starting Transmitter...");
        
            while(!stopped()) {
                // Wait for commands from wpilib to come in.
                while(queue.isEmpty());
                data = queue.poll();
                System.out.println("Received from main thread: " + data);

                try {
                    output.writeBytes(data +"\n");
                    Thread.currentThread().sleep(10);
                } catch(Exception ex) {
                    ex.printStackTrace();
                }
            }
        }

        private synchronized boolean stopped() {
            return shouldStop;
        }

        public synchronized void stopThread() {
            shouldStop = true;
        }
    }

    // the Receiver class gets data off the Raspberry Pi and puts it onto the queue.
    static class Receiver implements Runnable {
        private ConcurrentHashMap<String, ConcurrentLinkedQueue<String>> queues;
        private DatagramSocket socket;

        private byte[] rawData;
        private boolean shouldStop;

        Receiver(ConcurrentHashMap<String, ConcurrentLinkedQueue<String>> queues){
            System.out.println("Creating Receiver...");
            try {   // Initialize UDP socket here.
                socket = new DatagramSocket(5806, InetAddress.getByName("0.0.0.0"));
                socket.setSoTimeout(10);
                System.out.println("UDP Socket ready for reception");
            } catch(Exception ex) {
                System.err.println("UDP Socket connection error:"+ ex);
            }
            
            this.queues = queues;
            shouldStop = false;
        }

        private void enqueueData(String data) {
            String[] string = data.split("\\+", 3);
            queues.get(string[1]).add(string[2]);
        }
        
        private String getPacket() {
            rawData = new byte[64];
            DatagramPacket packet = new DatagramPacket(rawData, rawData.length);
            try {
                this.socket.receive(packet);
            } catch(Exception ex) {
                //ex.printStackTrace();
            }
            
            String parsed = new String(packet.getData()).trim();

            if(parsed.length() > 0)
                return parsed;
            else
                return null;
        }

        public void run() {
            String data;
            System.out.println("Starting Receiver...");

            try {
                while(!stopped()) {
                    data = getPacket();

                    if(data != null) {
                        System.out.println("Received from socket: " + data);
                        enqueueData(data);
                    }

                    Thread.currentThread().sleep(20);
                }
            } catch(Exception ex) {
                ex.printStackTrace();
            }
        }

        private synchronized boolean stopped() {
            return shouldStop;
        }

        public synchronized void stopThread() {
            shouldStop = true;
        }
    }

    // Constructor to setup all queues, sockets, and threads.
    Transceiver() {
        System.out.println("Start constructor");
        outboundQueue = new ConcurrentLinkedQueue<String>();
        
        inboundQueues = new ConcurrentHashMap<String, ConcurrentLinkedQueue<String>>();
        inboundQueues.put("Cube", new ConcurrentLinkedQueue<String>());
        inboundQueues.put("Tape", new ConcurrentLinkedQueue<String>());
        inboundQueues.put("Vault", new ConcurrentLinkedQueue<String>());
        
        // Starting threads.
        transmitter = new Thread(new Transmitter(outboundQueue));
        transmitter.start();

        receiver = new Thread(new Receiver(inboundQueues));
        receiver.start();
        
        System.out.println("End constructor");
    }

    /*
        enableTargeting(string target), disableTargeting(string target)
        ---------------------------------------------------------------
        
        Tells the robot to start one of several image processing algorithms.
        Pass in the following strings to start specific algorithms:

        "Cube"  -   Enables the cube detection algorithm for picking up cubes.
        "Tape"  -   Enables the tape detection algorithm for lining the robot up with the switch.
        "Vault" -   Enables the vault detection algorithm for lining cubes up with the vault.
    */
    public void enableTargeting(String target) {
        flushQueue(target);
        outboundQueue.add("command+"+ target +"+startTargeting");
    }

    public void disableTargeting(String target) {
        outboundQueue.add("command+"+ target +"+stopTargeting");
        flushQueue(target);
    }

    private void flushQueue(String queue) {
        // Empty queue by discarding extra data.
        while(!inboundQueues.get(queue).isEmpty())
            inboundQueues.get(queue).poll();
    }

    /*
        getData(string type)
        --------------------

        Get data from Raspberry Pi. Pass in "Cube", "Tape", or "Vault" for specific data.

        May return null values that need to be checked for.
    */
    public Integer getData(String type) {
        String data = inboundQueues.get(type).poll();
        
        if(data == null)
            return null;
        else
            return Integer.parseInt(data);
    }

    /*
    public void shutdown() {
        transmitter.stopThread();
        receiver.stopThread();
    }
    */
}




