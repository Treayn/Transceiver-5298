//package FRC;
//import Transceiver.java;

public class First {
    public static void main(String[] args) {
        try {
            Transceiver transceiver = new Transceiver();
            for(int i = 0; i < 10; i++) {
                transceiver.enableTargeting("Cube");
            }

            while(true) {
                Integer p = transceiver.getData("Cube");
                if(p != null)
                    System.out.println("Main Thread Data:"+ p);
                Thread.currentThread().sleep(100);
            }

        } catch(Exception ex) {
            ex.printStackTrace();
        }

        
    }
}
