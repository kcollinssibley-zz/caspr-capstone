"""
Implementation of a Disentangled Representation learning Generative
Adversarial Networks. This includes models for both the generator 
encoder decoder and the discriminator as well as the models that
are used to train these networks.
"""

import numpy as np
import time 

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Reshape
from keras.layers import Conv2D, Conv2DTranspose, UpSampling2D
from keras.layers import LeakyReLU, Dropout, AveragePooling2D
from keras.layers import BatchNormalization
from keras.optimizers import Adam, RMSprop, SGD

import matplotlib.pyplot as plt

class DRGAN(object):
    """ This calss will contain all the networks and models in order
        to train and operate a DRGAN as well as the functions to initialize 
        and acces the individual networks and models
    """
    
    def __init__(self, img_rows=96, img_cols=96, img_channels=1):
        #Store shape info
        self.img_rows = img_rows
        self.img_cols = img_cols
        self.img_channels = img_channels

        #
        self.img_shape = (img_rows, img_cols, img_channels)
        
        self.D = None 
        self.G_enc = None
        self.G_dec = None
        self.G = None

        self.AM = None
        self.DM = None

    def generator_enc(self):
        if self.G_enc is not None:
            return self.G_enc

        #Initialize sequential model
        self.G_enc = Sequential()

        self.G_enc.add(Conv2D(32, 3, padding='same',\
                        input_shape=self.img_shape))
        self.G_enc.add(Conv2D(64, 3, padding='same'))
        
        self.G_enc.add(Conv2D(64, 3, strides=2, padding='same'))
        self.G_enc.add(Conv2D(64, 3, padding='same'))
        self.G_enc.add(Conv2D(128, 3, padding='same'))

        self.G_enc.add(Conv2D(128, 3, strides=2, padding='same'))
        self.G_enc.add(Conv2D(96, 3, padding='same'))
        self.G_enc.add(Conv2D(192, 3, padding='same'))

        self.G_enc.add(Conv2D(192, 3, strides=2, padding='same'))
        self.G_enc.add(Conv2D(128, 3, padding='same'))
        self.G_enc.add(Conv2D(256, 3, padding='same'))

        self.G_enc.add(Conv2D(256, 3, strides=2,padding='same'))
        self.G_enc.add(Conv2D(160, 3, padding='same'))
        self.G_enc.add(Conv2D(320, 3, padding='same'))
        
        self.G_enc.add(AveragePooling2D(pool_size=6, padding='same'))
        self.G_enc.summary()
        return self.G_enc

    def generator_dec(self):
        if self.G_dec is not None:
            return self.G_dec

        self.G_dec = Sequential()

        self.G_dec.add(Dense(320, input_shape=(1,1,320)))
        
        self.G_dec.add(LeakyReLU(alpha=0.2))
        self.G_dec.add(Dropout(dropout))
        
        self.G_dec.add(UpSampling2D(6))
        self.G_dec.add(Conv2D(160, 3, padding='same'))
        self.G_dec.add(Conv2D(256, 3, padding='same'))
       
        self.G_dec.add(LeakyReLU(alpha=0.2))
        self.G_dec.add(Dropout(dropout))

        self.G_dec.add(UpSampling2D())
        self.G_dec.add(Conv2D(256, 3, padding='same'))
        self.G_dec.add(Conv2D(128, 3, padding='same'))
        self.G_dec.add(Conv2D(192, 3, padding='same'))

        self.G_dec.add(LeakyReLU(alpha=0.2))
        self.G_dec.add(Dropout(dropout))

        self.G_dec.add(UpSampling2D())
        self.G_dec.add(Conv2D(192, 3, padding='same'))
        self.G_dec.add(Conv2D(96, 3, padding='same'))
        self.G_dec.add(Conv2D(128, 3, padding='same'))

        self.G_dec.add(LeakyReLU(alpha=0.2))
        self.G_dec.add(Dropout(dropout))

        self.G_dec.add(UpSampling2D())
        self.G_dec.add(Conv2D(128, 3, padding='same'))
        self.G_dec.add(Conv2D(64, 3, padding='same'))
        self.G_dec.add(Conv2D(64, 3, padding='same'))

        self.G_dec.add(LeakyReLU(alpha=0.2))
        self.G_dec.add(Dropout(dropout))

        self.G_dec.add(UpSampling2D())
        self.G_dec.add(Conv2D(64, 3, padding='same'))
        self.G_dec.add(Conv2D(32, 3, padding='same'))
        self.G_dec.add(Conv2D(1, 3, padding='same'))
        
        self.G_dec.add(LeakyReLU(alpha=0.2))
        self.G_dec.add(Dropout(dropout))

        self.G_dec.summary()
        return self.G_dec

    def generator(self):
        if self.G is not None:
            return self.G

        self.G = Sequential()
        self.G.add(self.generator_enc())
        self.G.add(self.generator_dec())

        return self.G
   
    def discriminator(self):
        if self.D:                                                             
            return self.D                                                      
        self.D = Sequential()                                                  
        self.D.add(self.generator_enc())  

        self.D.add(Flatten())
        self.D.add(Dense(320))

         # Out: 1-dim probability
        self.D.add(Dense(1))
        self.D.add(Activation('sigmoid'))    
                                                     
        return self.D

    def adversarial_model(self):
        if self.AM:                                                             
            return self.AM                                                      
        optimizer = SGD(lr=0.002, momentum=.9)                                  
        self.AM = Sequential()     
        self.AM.add(self.generator())
        self.AM.add(self.discriminator())                                       
        self.AM.compile(loss='binary_crossentropy', optimizer=optimizer,\
            metrics=['accuracy'])                                               
        return self.AM   

    def discriminator_model(self):
        if self.DM:                                                             
            return self.DM                                                      
        optimizer = SGD(lr=0.002, momentum=.9)                                  
        self.DM = Sequential()                                                  
        self.DM.add(self.discriminator())                                       
        self.DM.compile(loss='binary_crossentropy', optimizer=optimizer,\
            metrics=['accuracy'])                                               
        return self.DM  


