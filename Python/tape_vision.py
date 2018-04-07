import cv2
import numpy as np

class TapeVision(object):
    def __init__(self, port: int, width: int, height: int):
        # Set camera port.
        self.camera = cv2.VideoCapture(port)

        # Set camera resolution.
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # Center of camera is our target position.
        self.targetPosition = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
        self.height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)
        
        # Set bounds for color filtering.
        self.bounds = {
            "upper": np.array([150, 32, 255]),
            "lower": np.array([90, 0, 224])
        }

        # List for running average, 4 indexes, each initialized to 0.
        self.samples = [0] * 4
    
    def _capture_frame(self) -> None:
        _, self.frame = self.camera.read()
    
    def _overlay_target(self):
        cv2.circle(self.frame, (self.targetPosition, self.height), 7, (0, 255, 0), -1)
        cv2.putText(self.frame, "Robot Center", (self.targetPosition, self.height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    def _threshold_image(self):
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        self.mask = cv2.inRange(hsv, self.bounds["lower"], self.bounds["upper"])
    
    def _get_contours(self):
        bw, contours, hierarchy = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
        hulls = [cv2.convexHull(contour) for contour in contours]
        
        sortedContours = sorted(hulls, key=cv2.contourArea)
        self.filteredContours = sortedContours[-2:]
        cv2.drawContours(self.frame, self.filteredContours, -1, (0,255,0), 3)
    
    def _get_centers(self):
        contourCenters = list(map(lambda center: cv2.moments(center), self.filteredContours))
        self.contourX = list(map(lambda point: int(point["m10"]/point["m00"]), contourCenters))
        self.currentPosition = int((self.contourX[0] + self.contourX[1])/2)
        print('Current position: ' + str(self.currentPosition))
        print('Target position: ' + str(self.targetPosition))
    
    def _overlay_actual(self):
        cv2.circle(self.frame, (self.currentPosition, self.height), 7, (0, 0, 255), -1)
        cv2.putText(self.frame, "Target Position", (self.currentPosition, self.height + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    def _filter_results(self):
        del self.samples[0]
        self.samples.append(self.currentPosition - self.targetPosition)
        self.dx = np.mean(self.samples)
        self.filteredPosition = int(round(self.dx + self.targetPosition))
    
    def _overlay_filtered(self):
        cv2.circle(self.frame, (self.filteredPosition, self.height), 7, (255, 0, 0), -1)
        cv2.putText(self.frame, "Target Filtered", (self.filteredPosition + 20, self.height), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    def _display_results(self):
        cv2.imshow('Raw', self.frame)
        cv2.waitKey(1)
    
    def _save_frame(self):
        self.output.write(frame)

    def _getError(self):
        return self.dx
        #return (self.dx*255)/(targetPosition*2)
    
    def free_resources(self):
        self.camera.release()
        self.output.release()
        cv2.destroyAllWindows()

    def process(self):
        self._capture_frame()
        self._overlay_target()
        self._threshold_image()
        try:
            self._get_contours()
            self._get_centers()
        except (IndexError, ZeroDivisionError) as e:
            self.currentPosition = self.targetPosition
            print('ERROR: No contours detected')
            print('Using default target coordinates:' + str(self.targetPosition))
        self._overlay_actual()
        self._filter_results()
        self._overlay_filtered()
        self._display_results()
        return self._getError()