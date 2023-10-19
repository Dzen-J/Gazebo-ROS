#!/usr/bin/env python

import rospy
import math
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from gazebo_msgs.srv import GetModelState
from tf.transformations import euler_from_quaternion
from sensor_msgs.msg import LaserScan

def _get_coords(name):
    model_coordinates = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState) 
    resp_coordinates = model_coordinates(str(name),'world')
    return resp_coordinates.pose.position
pos = _get_coords('rosbots')
print('\ninitial coordinates of the robot:')
print(pos.x, pos.y)
print('\nEnter the coords:')
x, y = map(float, input().split())



rospy.init_node('command_node', anonymous=True)
pub = rospy.Publisher('/part2_cmr/cmd_vel', Twist, queue_size=10)
twist_msg = Twist()
theta = 0  
EPSILON = 0.2

def odom_callback(msg):
    global twist_msg, theta
    orientation_q = msg.pose.pose.orientation
    orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
    roll, pitch, yaw = euler_from_quaternion(orientation_list)
    theta = yaw
    return theta
rospy.Subscriber('/odom',Odometry, odom_callback)

left_ranges = 0
right_ranges = 0
center_ranges = 0

def laser_callback(data):
    global left_ranges 
    global right_ranges
    global center_ranges
    
    # Разделим область видимости лидара на три части: левая, центральная и правая.
    left_ranges = min(data.ranges[:len(data.ranges) // 3])
    center_ranges = min(data.ranges[len(data.ranges) // 4 : 3 * len(data.ranges) // 4])
    right_ranges = min(data.ranges[2 * len(data.ranges) // 3 :])
    

rospy.Subscriber("/bot_0/laser/scan", LaserScan, laser_callback)
rate = rospy.Rate(10)  # 10hz

def ob(left_ranges, center_ranges, right_ranges):
    if center_ranges > 2 or right_ranges > 2 or left_ranges > 2:
        if left_ranges > right_ranges:
            if center_ranges < 1:
                twist = Twist()
                twist.linear.x = 0
                twist.angular.z = -0.3
                pub.publish(twist)
                rospy.sleep(0.5)
            elif right_ranges < 1:
                twist = Twist()
                twist.linear.x = 0.3
                twist.angular.z = 0
                pub.publish(twist)
                rospy.sleep(0.5)
        else:
            if center_ranges < 1:
                twist = Twist()
                twist.linear.x = 0
                twist.angular.z = 0.3
                pub.publish(twist)
                rospy.sleep(0.5)
            elif left_ranges < 1:
                twist = Twist()
                twist.linear.x = 0.3
                twist.angular.z = 0
                pub.publish(twist)
                rospy.sleep(0.5)
def main():
    pub.publish(twist_msg)
    status = 0
    target_x, target_y = x, y
    pos = _get_coords('rosbots')
    current_x, current_y = pos.x, pos.y
    angle = math.atan2(target_y - current_y, target_x - current_x) - theta
    distance = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
    while distance > EPSILON:
     ob(left_ranges, center_ranges, right_ranges)
     while abs(angle) > 0.2:
          ob(left_ranges, center_ranges, right_ranges)
          pos = _get_coords('rosbots')
          current_x, current_y = pos.x, pos.y
          angle = math.atan2(target_y - current_y, target_x - current_x) - theta
          twist = Twist()
          twist.angular.z = 0.5 * angle
          pub.publish(twist)
     ob(left_ranges, center_ranges, right_ranges)
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
