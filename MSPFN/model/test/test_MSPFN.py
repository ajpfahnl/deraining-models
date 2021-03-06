import numpy as np
import scipy
import cv2
import os
import glob
import time
import tensorflow as tf
import matplotlib.pyplot as plt
import sys
import argparse
sys.path.append('../')
sys.path.append('../../utils')
#from TEST_MSPFN import Model
from TEST_MSPFN_M17N1 import Model
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
is_training = tf.placeholder(tf.bool, [])

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', type=str, required=True)
parser.add_argument('--result_dir', type=str, required=True)
args = parser.parse_args()

img_path = args.input_dir #'./test_data/weathernet_small'
file = os.listdir(img_path)
save_path = args.result_dir #'./test_data/MSPFN_out/'

if not os.path.exists(save_path):
    os.mkdir(save_path)


num =1
for f in file:
    pic_path = os.path.join(img_path, f)
    print(f)
    file_name = f
    img = cv2.imread(pic_path)
    try:
        W, H = img.shape[:2]
    except:
        continue
    print(img.shape)
    img = img / 127.5 - 1
    input_ = np.zeros((1, W, H, 3))#16
    print(input_.shape)
    input_[0] = img
    if num==1:
        W_1 = W
        H_1 = H
        x_rain = tf.placeholder(tf.float32, [1, W, H, 3])#None
        model = Model(x_rain, is_training, 1)#16
        init = tf.global_variables_initializer()
        sess = tf.Session()
        sess.run(init)
        saver = tf.train.Saver()
        saver.restore(sess, '../MSPFN_pretrained/epoch44')#93
        vars_all=tf.trainable_variables()
        print ('Params:',np.sum([np.prod(v.get_shape().as_list()) for v in vars_all]))
        st_time=time.time()
        fake = sess.run(
            [model.imitation],
            feed_dict={x_rain: input_, is_training: False})
        ed_time=time.time()
        cost_time=ed_time-st_time
        print('spent {} s.'.format(cost_time))
    else:
        if W_1==W and H_1 == H:
            st_time=time.time()
            fake = sess.run(
                [model.imitation],
                feed_dict={x_rain: input_, is_training: False})
            ed_time=time.time()
            cost_time=ed_time-st_time
            print('spent {} s.'.format(cost_time))
        else:
            #sess.close()
            W_1 = W
            H_1 = H
            x_rain = tf.placeholder(tf.float32, [1, W, H, 3])#None
            model = Model(x_rain, is_training, 1)#16
            init = tf.global_variables_initializer()
            sess = tf.Session()
            sess.run(init)
            saver = tf.train.Saver()
            saver.restore(sess, '../MSPFN_pretrained/epoch44')#93
            st_time=time.time()
            fake = sess.run(
                [model.imitation],
                feed_dict={x_rain: input_, is_training: False})
            ed_time=time.time()
            cost_time=ed_time-st_time
            print('spent {} s.'.format(cost_time))
    img = fake[0]
    im = np.uint8(np.clip((img[0]+1)*127.5,0,255.0))
    cv2.imwrite(os.path.join(save_path, file_name), im)
    num+=1
