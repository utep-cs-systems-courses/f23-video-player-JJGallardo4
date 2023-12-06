import os
import cv2
import threading
import numpy as np
import base64
import sys

class Q:

    def __init__(self):
        self.Storage = []
        self.StorageLock = threading.Lock()
        self.Full = threading.Semaphore(0)
        self.Empty = threading.Semaphore(9999)

    def insert(self, item):
        self.Empty.acquire()
        self.StorageLock.acquire()
        self.Storage.append(item)
        self.StorageLock.release()
        self.Full.release()

    def remove(self):
        self.Full.acquire()
        self.StorageLock.acquire()
        item = self.Storage[0]
        self.Storage = self.Storage[1:]
        self.StorageLock.release()
        self.Empty.release()
        return item

def convertToGS(frame):
    if(frame is not None):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return None

def producer(fileName, q, maxFramesLoad = 9999):
    i = 0
    vidcap = cv2.VideoCapture(fileName)
    success, image = vidcap.read()
    while(success and i  < maxFramesLoad):
        
        success, jpgImage = cv2.imencode(".jpg", image)
        frame = convertToGS(image)
        
        if(frame is  None):
            print("Gray Scale not working")
            sys.exit()
        
        q.insert(frame)
        success, image = vidcap.read()
        i += 1

    print("Frame Extraction Complete")
        
def consumer(q):
    
    while( not (len(q.Storage) == 0)):
        frame = q.remove()

        cv2.imshow("Video", frame)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

    print("Displaying Frames Complete")
    cv2.destroyAllWindows()
    pass


fileName = "clip.mp4"

q = Q()

tProducer = threading.Thread(target = producer(fileName, q))
tConsumer = threading.Thread(target = consumer(q))


tProducer.start()
tConsumer.start()
