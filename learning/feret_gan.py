
'''
DCGAN on MNIST using Keras
Author: Rowel Atienza
Project: https://github.com/roatienza/Deep-Learning-Experiments
Dependencies: tensorflow 1.0 and keras 2.0
Usage: python3 dcgan_mnist.py
'''

import numpy as np
import os
import cv2
import scipy.ndimage as ndimg
import scipy.misc as sci_misc
import time

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Reshape
from keras.layers import Conv2D, Conv2DTranspose, UpSampling2D
from keras.layers import LeakyReLU, Dropout
from keras.layers import BatchNormalization
from keras.optimizers import Adam, RMSprop

import matplotlib.pyplot as plt
from drgan import DRGAN

DATABASE = "/home/matt/capstone/faces/"
OUT_DIR = "/home/matt/capstone/output/"

#Load an image from the data base and return it

class ElapsedTimer(object):
    def __init__(self):
        self.start_time = time.time()
    def elapsed(self,sec):
        if sec < 60:
            return str(sec) + " sec"
        elif sec < (60 * 60):
            return str(sec / 60) + " min"
        else:
            return str(sec / (60 * 60)) + " hr"
    def elapsed_time(self):
        print("Elapsed: %s " % self.elapsed(time.time() - self.start_time) )

class FERET_DRGAN(object):
    def __init__(self):
        self.img_rows = 96
        self.img_cols = 96
        self.channel = 3

        self.faces = dict()
        self.face_dims = dict()

        self.unknown_faces = []

        for filename in os.listdir(DATABASE):
            self.loadimage(filename)
            if len(self.faces) > 50:
                break

        for filename in self.unknown_faces:
            self.loadimage(filename, buffer_unknown=False)

        self.DRGAN = DRGAN()
        self.discriminator =  self.DRGAN.discriminator_model()
        self.adversarial = self.DRGAN.adversarial_model()
        self.generator = self.DRGAN.generator()

    def loadimage(self, filename, buffer_unknown=True):

        #Read in image stored under this filename
        img = cv2.imread((DATABASE+filename), 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

        #Extract the face's ID number from the filename
        face_no = int(filename[0:5])
        
        #If the character f is in the file name then it is a "frontal" image
        if 'f' in filename:
            #Locate the face
            _face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')                                                                           
            faces = _face_cascade.detectMultiScale(img, 1.3, 5)  

            #If it didn't find a face then just skip it 
            if len(faces) == 0:
                return

            #Initialize values
            max_area = 0
            best_face = -1

            #Find the largest face in the image
            for i in range(len(faces)):
                x, y, w, h = faces[i]
                if w*h > max_area:
                    max_area = w*h
                    best_face = i

            #Extract dimensions of the best face
            x, y, w, h = faces[best_face]

            #Crop image
            cropped_img = img[y:y+h,x:x+w,:]

            #Store the cropping info for this face
            self.face_dims[face_no] = (x, y, w, h) 

            #Resize the image 
            img = cv2.resize(cropped_img, (96,96))
            img = np.expand_dims(img, axis=0)

            if face_no in self.faces:
                self.faces[face_no].insert(0, img)
            else:
                self.faces[face_no] = [img]

        #If this is not a frontal image
        else:
            #If we have found the frontal shot of this subject just get the cropping dims
            if face_no in self.face_dims:
                x, y, w, h = self.face_dims[face_no]
            else:
                #If we don't know the frontal shot yet store this file name for later
                if buffer_unknown:
                    self.unknown_faces.append(filename)
                return None
            
            #Crop the image and resize
            cropped_img = img[y:y+h,x:x+w,:]
            img = cv2.resize(cropped_img, (96,96))
            img = np.expand_dims(img, axis=0)
            
            self.faces[face_no].append(img)


    def train(self, train_steps=2000, batch_size=16, save_interval=0):
        noise_input = None
        if save_interval>0:
            noise_input = np.random.uniform(0.0, 255.0, size=[16, 96, 96, 3])
        for i in range(train_steps):
            gen_train = np.zeros(shape=(1, 96, 96, 1))
            gen_labels = np.zeros(shape=(1, 96, 96, 1))

            #Randomly select a set of training images
            for i in range(batch_size):
                face_num = random.choice(self.faces.keys())
                gen_train = np.stack((gen_train, random.choice(self.faces[face_num])))
                gen_label = np.stack((gen_labels, self.faces[face_num][0]))

            gen_train = gen_train[1:, :, :, :]
            gen_label = gen_label[1:, :, :, :]

            #Generate an equal amount of noise images to generate from
            images_fake = self.generator.predict(gen_train)

            #Try to concatenate these into one data set
            x = np.concatenate((images_train, images_fake))
            #print "train images shape: {}".format(images_train.shape)
            #print "fake images shape: {}".format(images_fake.shape)

            #Create the labels y (1 for a real image and 0 for a fake image)
            y = np.ones([2*batch_size, 1])
            y[batch_size:, :] = 0

            #Train the discriminator model on this data set
            d_loss = self.discriminator.train_on_batch(x, y)

            y = np.ones(shape=(batch_size, 1))
            
            a_loss = self.adversarial.train_on_batch(gen_train, y)
            
            #Log losses from this round of training
            log_mesg = "{}: [D loss: {}, acc: {}]".format(i, d_loss[0], d_loss[1])
            log_mesg = "{}  [A loss: {}, acc: {}]".format(log_mesg, a_loss[0], a_loss[1])
            
            print(log_mesg)
            if save_interval>0:
                if (i+1)%save_interval==0:
                    self.plot_images(save2file=True, samples=noise_input.shape[0],\
                        noise=noise_input, step=(i+1))

    def plot_images(self, save2file=False, fake=True, samples=16, noise=None, step=0):
        filename = 'feret.png'
        if fake:
            if noise is None:
                noise = np.random.uniform(0.0, 255.0, size=[samples, 128, 128, 3])
            else:
                filename = "mnist_%d.png" % step
            images = self.generator.predict(noise)
        else:
            i = np.random.randint(0, self.x_train.shape[0], samples)
            images = self.x_train[i, :, :, :]

        for i in range(images.shape[0]):
            out_name = "{}{}_{}.jpg".format(OUT_DIR, step, i)
            image = images[i, :,:,:] * 255
            if i ==0:
                print image
            cv2.imwrite(out_name, image.astype('uint8'))


        """plt.figure(figsize=(10,10))
        for i in range(images.shape[0]):
            plt.subplot(4, 4, i+1)
            image = images[i, :, :, :]
            image = np.reshape(image, [self.img_rows, self.img_cols, self.channel])
            plt.axis('off')
        plt.tight_layout()
        if save2file:
            plt.savefig(filename)
            plt.close('all')
        else:
            plt.show()

            """

if __name__ == '__main__':
    feret_dcgan = FERET_DRGAN()
    timer = ElapsedTimer()
    feret_dcgan.train(train_steps=100000, batch_size=32, save_interval=50)
    timer.elapsed_time()
    feret_dcgan.plot_images(fake=True)
    feret_dcgan.plot_images(fake=False, save2file=True)
