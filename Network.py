from tensorflow.keras.layers import Dense,InputLayer,Conv2D,GlobalMaxPooling2D,Flatten,BatchNormalization
from tensorflow.keras import Model
from keras.models import Sequential
import numpy as np
import tensorflow as tf


def policy_loss(y_true ,y_pred):
    """"
    Y_true is expected to have the shape=(2,batch_size)=(advantages,actions) and is splited according to rows(axis=1)
    """
    #y_pred is already normalized(not logits)
    const_entropy=0.1
    log_p=tf.math.log(y_pred)#log(π)    
    adv,actions=tf.split(y_true,axis=1,num_or_size_splits=2)
    adv=tf.squeeze(tf.cast(adv,dtype="float32"),axis=-1)
    actions=tf.cast(actions,dtype="int32").numpy().squeeze(-1)
    actions=[[i,actions[i]] for i in range(log_p.shape[0])]
    log_p_g=tf.gather_nd(log_p,actions)#select the policy based on the action
    ll=-adv*log_p_g
    entropy=tf.math.reduce_mean(tf.math.reduce_sum(y_pred*log_p,axis=1))
    loss=tf.math.reduce_mean(ll,axis=0)

    return loss+const_entropy*entropy

class ActorCritic(tf.keras.Model):
    def __init__(self,in_shape,n_actions,**kwargs):
        super(ActorCritic,self).__init__(**kwargs)
        self.inpt=InputLayer(input_shape=in_shape,dtype="int32")
        self.Normal=BatchNormalization()
        self.lay1=Conv2D(filters=8,kernel_size=4,strides=2,padding="valid",activation="relu")
        self.lay2=Conv2D(filters=12,kernel_size=2,strides=1,padding="same",activation="relu")
        self.lay3=Conv2D(filters=12,kernel_size=3,strides=2,padding="valid",activation="relu")
        self.lay4=Conv2D(filters=24,kernel_size=3,strides=2,padding="valid",activation="relu")
        self.lay5=Conv2D(filters=42,kernel_size=2,strides=2,padding="valid",activation="relu")
        self.lay6=Conv2D(filters=1,kernel_size=1,strides=1,padding="same",activation="relu")
        self.flat=Flatten()
        self.head=Dense(100,activation="relu")
        self.head1=Dense(10,activation="relu")
        self.head2=Dense(10,activation="relu")
        self.critic=Dense(n_actions,activation="softmax")
        self.value=Dense(1,activation='linear')

    def call(self,x):
        x=self.inpt(x)
        x=self.Normal(x)
        x=self.lay1(x)
        x=self.lay2(x)
        x=self.lay3(x)
        x=self.lay4(x)
        x=self.lay5(x)
        x=self.lay6(x)
        x=self.flat(x)
        x=self.head(x)
        critic=self.critic(self.head1(x))
        value=self.value(self.head2(x))
        return critic,value

    def build_graph(self, raw_shape):
        #function for the visualization of model
        x = tf.keras.layers.Input(shape=raw_shape)
        return Model(inputs=[x], outputs=self.call(x))
