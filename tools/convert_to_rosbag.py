#!/usr/bin/env python
# -*- coding: utf8 -*-
import argparse
import os

import cv2
import rosbag
import sys

import time

import rospy
import yaml
from cv_bridge import CvBridge

from humanoid_league_msgs.msg import BallInImage, BallsInImage, LineSegmentInImage, LineInformationInImage, PostInImage, \
    GoalPartsInImage, BarInImage
from sensor_msgs.msg import Image
import std_msgs.msg


def create_img_msg(img_path, seq, stamp):
    image = cv2.imread(directory + "/" + img["name"])
    msg = bridge.cv2_to_imgmsg(image, "bgr8")
    msg.header.seq = seq
    msg.header.stamp = stamp
    return msg


def create_ball_msg(ball_label):
    msg = BallInImage()
    if float(ball_label["x"]) != 0:
        msg.center.x = float(ball_label["x"])
        msg.center.y = float(ball_label["y"])
        msg.diameter = float(ball_label["dia"])
        msg.confidence = 1.0
    else:
        msg.confidence = 0.0
    return msg


def create_balls_msg(ball_msgs, seq, stamp):
    msg = BallsInImage()
    msg.header.seq = seq
    msg.header.stamp = stamp
    msg.candidates = ball_msgs
    return msg


def create_post_msg(post_label):
    msg = PostInImage()
    if float(post_label["x"]) != 0:
        msg.confidence = 1.0
        msg.foot_point.x = float(post_label["x"])
        msg.foot_point.y = float(post_label["y"])
        msg.width = int(post_label["width"])
    else:
        msg.confidence = 0.0
    return msg


def create_bar_msg(bar_label):
    msg = BarInImage()
    if float(bar_label["x"]) != 0:
        msg.confidence = 1.0
        msg.width = int(bar_label["width"])
        msg.left_point.x = float(bar_label["lx"])
        msg.left_point.y = float(bar_label["ly"])
        msg.right_point.x = float(bar_label["rx"])
        msg.right_point.y = float(bar_label["ry"])
    else:
        msg.confidence = 0.0
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

parser = argparse.ArgumentParser(prog="convert_to_rosbag", description="This script creates a rosbag file out of "
                                                                       "images and labels which are exported from the "
                                                                       "Hamburg Bit-Bots imagetagger. Please call the "
                                                                       "script by providing a path to the folder "
                                                                       "which contains the images. If not it will "
                                                                       "search in the current directory. The label "
                                                                       "file has to be called labels.yaml and be "
                                                                       "located in the same folder. Second argument "
                                                                       "is an optional path and name for the bag "
                                                                       "file. If it is not provided, the bag will be "
                                                                       "saved in the current directory with a default "
                                                                       "name. ")
parser.add_argument('directory', nargs='?', default=os.getcwd(),
                    help='Directory path were images and labels.yaml are located. If none is provided, the current '
                         'working dir will be used.')
parser.add_argument('bag_path', nargs='?', default=os.getcwd() + "/" + time.strftime("%Y%m%d-%H%M%S") + ".bag",
                    help="Path and name of the bagfile. If none is provided a file will be generated in the current "
                         "working dir.")
parser.add_argument('-i', dest='image', action='store_true',
                    help='Activates export of images.')
parser.add_argument('-b', dest='ball', action='store_true',
                    help='Activates export of balls.')
parser.add_argument('-g', dest='goal', action='store_true',
                    help='Activates export of goal related labels.')
args = parser.parse_args()
directory = args.directory
bag_path = args.bag_path

if not args.image:
    print("Export of images not activated.")

if not args.ball:
    print("Export of balls not activated.")

if not args.goal:
    print("Export of goals not activated.")

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
    if args.image:
        img_msg = create_img_msg(directory + "/" + img["name"], seq, stamp)
        bag.write("/image", img_msg)
    labels = img["labels"]
    ball_msgs = []
    post_msgs = []
    bar_msgs = []
    for label in labels:
        if label["type"] == "ball" and args.ball:
            ball_msg = create_ball_msg(label)
            bag.write("/ball_in_image", ball_msg)
            ball_msgs.append(ball_msg)
        elif label["type"] == "post" and args.goal:
            post_msg = create_post_msg(label)
            # bag.write("/post_in_image", post_msg)
            post_msgs.append(post_msg)
        elif label["type"] == "bar" and args.goal:
            bar_msg = create_bar_msg(label)
            bar_msgs.append(bar_msg)
    if args.ball:
        balls_msg = create_balls_msg(ball_msgs, seq, stamp)
        bag.write("/ball_candidates", balls_msg)
    if args.goal:
        goal_parts_msg = create_goal_msg(post_msgs, bar_msgs, seq, stamp)
        bag.write("/goal_parts_in_image", goal_parts_msg)
    seq += 1

bag.flush()
bag.close()
bag.reindex()

print("\n Finished writing rosbag to " + bag_path)
