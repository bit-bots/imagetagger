#!/usr/bin/env python
# -*- coding: utf8 -*-
import os

import cv2
import rosbag
import sys

import time

import rospy
import yaml
from cv_bridge import CvBridge

from humanoid_league_msgs.msg import BallInImage, BallsInImage, LineSegmentInImage, LineInformationInImage, PostInImage, GoalPartsInImage, BarInImage
from sensor_msgs.msg import Image
import std_msgs.msg

"""
This script creates a rosbag file out of images and labels which are exported from the Hamburg Bit-Bots imagetagger. 
Please call the script by providing a path to the folder which contains the images. If not it will search in the 
current directory. The label file has to be called labels.yaml and be located in the same folder.
Second argument is an optional path and name for the bag file. If it is not provided, the bag will be saved in the 
current directory with a default name.  
"""


def create_img_msg(img_path, seq, stamp):
    image = cv2.imread(directory + "/" + img["name"])
    msg = bridge.cv2_to_imgmsg(image, "bgr8")
    msg.header.seq = seq
    msg.header.stamp = stamp
    return msg


def create_ball_msg(ball_label):
    msg = BallInImage()
    msg.center.x = float(ball_label["x"])
    msg.center.y = float(ball_label["y"])
    msg.diameter = float(ball_label["dia"])
    msg.confidence = 1.0
    return msg

def create_balls_msg(ball_msgs, seq, stamp):
    msg = BallsInImage()
    msg.header.seq = seq
    msg.header.stamp = stamp
    msg.candidates = ball_msgs
    return msg


def create_post_msg(post_label):
    msg = PostInImage()
    msg.confidence = 1.0
    msg.foot_point.x = float(post_label["x"])
    msg.foot_point.y = float(post_label["y"])
    msg.width = int(post_label["width"])
    return msg

def create_bar_msg(bar_label):
    msg = BarInImage()
    msg.confidence = 1.0
    msg.width = int(bar_label["width"])
    msg.left_point.x = float(bar_label["lx"])
    msg.left_point.y = float(bar_label["ly"])
    msg.right_point.x = float(bar_label["rx"])
    msg.right_point.y = float(bar_label["ry"])
    return msg

def create_goal_msg(post_msgs, bar_msgs, seq, stamp):
    msg = GoalPartsInImage()
    msg.header.seq = seq
    msg.header.stamp = stamp
    msg.posts = post_msgs
    msg.bars = bar_msgs
    return msg


###
### Parse arguments
###
arguments = sys.argv
if len(sys.argv) > 1:
    directory = arguments[1]
else:
    directory = os.getcwd()
if len(sys.argv) > 2:
    bag_path = arguments[2]
else:
    time_str = time.strftime("%Y%m%d-%H%M%S")
    bag_path = os.getcwd() + "/" + time_str + ".bag"

###
### Read label yaml file
###
try:
    with open(directory + "/" + "labels.yaml", 'r') as stream:
        label_yaml = yaml.load(stream)
        header = label_yaml["header"]
        print("Parsed labels for imageset " + header["imageset"])
        content = label_yaml["content"]
except FileNotFoundError:
    print("The label yaml file was not found. Please make sure that it is in the same folder as the images and "
          "called labels.yaml")
    exit(1)

###
### Create rosbag
###
bag = rosbag.Bag(bag_path, "w", compression='bz2')
bridge = CvBridge()

seq = 0
for img in content:
    sys.stdout.write("\rWriting image number " + str(seq))
    sys.stdout.flush()
    stamp = rospy.Time.from_sec(time.time())
    img_msg = create_img_msg(directory + "/" + img["name"], seq, stamp)
    bag.write("/image", img_msg)
    labels = img["labels"]
    ball_msgs = []
    post_msgs = []
    bar_msgs = []
    for label in labels:
        if label["type"] == "ball":
            ball_msg = create_ball_msg(label)
            bag.write("/ball_in_image", ball_msg)
            ball_msgs.append(ball_msg)
        elif label["type"] == "post":
            post_msg = create_post_msg(label)
            #bag.write("/post_in_image", post_msg)
            post_msgs.append(post_msg)
        elif label["type"] == "bar":
            bar_msg = create_bar_msg(label)
            bar_msgs.append(bar_msg)
    balls_msg = create_balls_msg(ball_msgs, seq, stamp)
    bag.write("/ball_candidates", balls_msg)
    goal_parts_msg = create_goal_msg(post_msgs, bar_msgs, seq, stamp)
    bag.write("/goal_parts_in_image", goal_parts_msg)
    seq += 1

bag.flush()
bag.close()
bag.reindex()

print("\n Finished writing rosbag to " + bag_path)