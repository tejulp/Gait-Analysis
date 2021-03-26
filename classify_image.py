#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 26 12:18:29 2018

@author: tejulpandit
"""
import tensorflow as tf
import sys

def get_labels():
    """Get the labels our retraining created."""
    with open('Desktop/tensorflow_for_gait/tf_files/retrained_labels.txt', 'r') as fin:
        labels = [line.rstrip('\n') for line in fin]
        return labels

def predict_on_image(image, labels):

    # Unpersists graph from file
    with tf.gfile.FastGFile("Desktop/tensorflow_for_gait/tf_files/retrained_graph.pb", 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')

    with tf.Session() as sess:
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

        # Read in the image_data
        image_data = tf.gfile.FastGFile("Desktop/tensorflow_for_gait/tf_files/test/di_a_12.jpg", 'rb').read()

        try:
            predictions = sess.run(softmax_tensor, \
                 {'DecodeJpeg/contents:0': image_data})
            prediction = predictions[0]
        except:
            print("Error making prediction.")
            sys.exit()

        # Return the label of the top classification.
        prediction = prediction.tolist()
        max_value = max(prediction)
        max_index = prediction.index(max_value)
        predicted_label = labels[max_index]
        
        return predicted_label