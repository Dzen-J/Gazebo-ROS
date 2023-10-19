#!/usr/bin/env python3

import rospy
import math
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from gazebo_msgs.srv import GetModelState
from tf.transformations import euler_from_quaternion

def _get_coords(name):
    model_coordinates = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState) 
    resp_coordinates = model_coordinates(str(name),'world')
    return resp_coordinates.pose.position
pos = _get_coords('rosbots')
print('\ninitial coordinates of the robot:')
print(pos.x, pos.y)
print('\nEnter the coords:')
x, y = map(float, input().split())



twist_msg = Twist()
theta = 0  
EPSILON = 0.1

def odom_callback(msg):
    global twist_msg, theta
    orientation_q = msg.pose.pose.orientation
    orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
    roll, pitch, yaw = euler_from_quaternion(orientation_list)
    theta = yaw
    return theta
    

rospy.init_node('command_node', anonymous=True)
rospy.Subscriber('/odom',Odometry, odom_callback)
rate = rospy.Rate(10)  # 10hz

def main():
    pub = rospy.Publisher('/part2_cmr/cmd_vel', Twist, queue_size=10)
    pub.publish(twist_msg)
    target_x, target_y = x, y
    pos = _get_coords('rosbots')
    current_x, current_y = pos.x, pos.y
    angle = math.atan2(target_y - current_y, target_x - current_x) - theta
    distance = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
    	    	
    while distance > EPSILON:
	    while abs(angle) > EPSILON:
    	    	pos = _get_coords('rosbots')
    	    	current_x, current_y = pos.x, pos.y
    	    	angle = math.atan2(target_y - current_y, target_x - current_x) - theta
    	    	twist = Twist()
    	    	twist.angular.z = 0.5 * angle
    	    	pub.publish(twist)
	    pos = _get_coords('rosbots')
	    current_x, current_y = pos.x, pos.y
	    distance = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
	    angle = math.atan2(target_y - current_y, target_x - current_x) - theta
	    twist = Twist()
	    twist.linear.x = 0.5
	    twist.angular.z = 0 
	    pub.publish(twist)	    	
    twist = Twist()
    twist.linear.x = 0
    pub.publish(twist)
    rate.sleep()
main()

pos = _get_coords('rosbots')
print('\nFinish coords:\n', pos.x, pos.y)
  
    
    
    
    
