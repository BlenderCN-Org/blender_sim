#!/usr/bin/env python

#python system imports
import threading
import sys
import traceback

#ros imports
import rospy


class StaticPublisher():
    def __init__(self):
        self.publisher = {}
        self.messages = {}
        self.time_stamped_msgs = {}
        self.thread = None    
        self.dataLock = threading.Lock()
    
    def __start_thread(self):
        self.thread = threading.Thread(target=self.__publisher, args=())
        self.thread.daemon = True
        self.thread.start()


    def __is_thread_running(self):
        return self.thread is not None
        
    def __publisher(self):
        r = rospy.Rate(100)
        while not rospy.is_shutdown():
            self.dataLock.acquire()
            if len(self.publisher) <= 0:
                self.dataLock.release()
                break
            else:
                for _, (pub, msg, time_stamped) in {topic : (self.publisher[topic], self.messages[topic], self.time_stamped_msgs[topic]) for topic in self.publisher.keys()}.items():
                    try:
                        if not rospy.is_shutdown():
                            if time_stamped:
                                msg.header.stamp = rospy.Time.now()
                            pub.publish(msg)
                    except Exception:
                        traceback.print_exc()
                self.dataLock.release()
                r.sleep()
                
        self.thread = None
        
        
    def publish(self, topic, message=None, time_stamped=False):
        self.dataLock.acquire()
        if message is None:
            pub = self.publisher.pop(topic, None)
            if pub is not None:
                pub.unregister()
        else:
            if not self.__is_thread_running():
                self.__start_thread()
            if not topic in self.publisher:
                self.publisher[topic] = rospy.Publisher(topic, type(message), queue_size=1)
            self.messages[topic] = message
            self.time_stamped_msgs[topic] = time_stamped
        self.dataLock.release()
        
    def __del__(self):
        self.cleanup()
        
    def cleanup(self):
        for topic in self.publisher.keys():
            try:
                self.publish(topic, None)
            except:
                pass

global_pub = StaticPublisher()

def publish(topic, message=None, time_stamped=False):
    global global_pub
    global_pub.publish(topic, message)
    
def stopPublish(topic):
    global global_pub
    global_pub.publish(topic, None)
    
def stopAllPublsh():
    global global_pub
    global_pub.cleanup()
