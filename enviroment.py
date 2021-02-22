import tensorflow as tf
import win32con
import win32api
from time import sleep
import numpy as np
from PIL import ImageGrab
import os
import pyautogui
import keyboard
import cv2
import subprocess

"""
A library that captures the game's state and sends "moves" to it. 

Main issue is finding the proper times for pressing and releasing the "buttons" so on the game be able to applying the correct action that we want.
Times for each move is based on the experimentation with the game and it is possibly that they will fail for others users.

Also,sometimes when health goes to zero the game is not ended and the enviroment can handle this situation by waiting both healths become full. Furthermore,
It can infer properly when there is a draw.
"""

def key_do(keys, frame_repeat=2):
        for key in keys:
            win32api.keybd_event(key,0,0,0)
        sleep(frame_repeat*0.2)
        for key in keys:
            win32api.keybd_event(key,0,win32con.KEYEVENTF_KEYUP,0)

def do_action(keys):
        for i,key in enumerate(keys[0]):
            keyboard.press(key)
            if i!=2:sleep(keys[1])
        for key in keys[0]:
            keyboard.release(key)
            sleep(keys[2])

class Enviroment():
    def __init__(self,coord):
        self.coordinates=coord
        self.end_net=tf.keras.models.load_model(r"\fighter\loss.h5")#network which infer if you lost or win(based on if there is a "hand" on the image)
        self.movements={
    "left":[["left"],0.30,0.0,0.50]
    ,"left-up":[["left","up"],0.30,0.0,0.85]
    ,"right-up":[["right","up"],0.30,0.0,0.85]
    ,"right":[["right"],0.30,0.0,0.5]
    ,"up":[["up"],0.25,0.0,0.8]
    ,"down":[["down"],0.5,0.0,0.25]
    ,"hard-punch": [["shift"],0.1,0.0,0.75]
    ,"light-punch": [["c"],0.1,0.0,0.75]
    ,"medium-punch":[["v"],0.1,0.0,0.75]
    ,"hard-kick":[["ctrl"],0.1,0.0,1]
    ,"medium-kick":[["z"],0.1,0.0,0.75]
    ,"light-kick":[["x"],0.1,0.0,0.75]
    ,"left-throw":[["left","ctrl"],0.05,0.01,1.75]
    ,"right-throw":[["right","ctrl"],0.05,0.01,1.75]
    ,"right-fireball":[["down","right","v"],0.025,0.025,1.75]
    ,"left-fireball":[["down","left","v"],0.025,0.025,1.5]
    ,"left-hurr-kick":[["down","left","z"],0.025,0.025,1.75]
    ,"right-hurr-kick":[["down","right","z"],0.025,0.025,1.75]
    ,"low-heavy-kick":[["down","ctrl"],0.025,0.025,1]
    ,"low-medium-kick":[["down","z"],0.025,0.025,0.75]
    ,"low-light-kick":[["down","x"],0.025,0.025,0.75]
    ,"low-heavy-punch":[["down","shift"],0.025,0.025,1]
    ,"low-medium-punch":[["down","v"],0.025,0.025,1]
    ,"low-light-punch":[["down","c"],0.025,0.025,1]
}
        self.names_move=list(self.movements.keys())
    def start_game(self,Open=True):
        self.wins=0
        self.loss=0
        self.health=100
        self.enemy_health=100
        self.done=False
        self.reward_end=0
        if Open:self.Open_game()
        self.wind=pyautogui.getWindowsWithTitle("snes9x")[0]
        try:
            self.wind.activate()
        except:
            pass
        self.state=np.asarray(ImageGrab.grab(self.coordinates))#default: x=8,y=95,w=512,h=475
        return self.state
    
    def Open_game(self):
        def leftClick():
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
            sleep(.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
        os.chdir(r"C:\Users\PROROAD\Desktop")
        subprocess.Popen(["snes9x-x64"],   stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        win32api.SetCursorPos((15,42))
        sleep(0.5)
        leftClick()
        sleep(0.5)
        win32api.SetCursorPos((40,85))
        leftClick()
        sleep(0.5)
        win32api.SetCursorPos((400,85))
        leftClick()
        sleep(10)
        wind=pyautogui.getWindowsWithTitle("snes9x")[0]
        wind.activate()
        key_do([32])
        sleep(1)
        key_do([32])
        sleep(0.5)
        key_do([40])
        sleep(0.5)
        key_do([32])
        sleep(0.5)
        key_do([32])
        sleep(2)
        key_do([32])
        sleep(13)
        key_do([32])


    

    def take_state(self,infer=True):
        self.state=np.asarray(ImageGrab.grab(self.coordinates))
        if infer:
            health_ima= self.state[26:41,64:236,:]#coordinates of where health is
            enemy_health_ima=self.state[26:41,268:440,:]
            self.health=self.take_health(health_ima)#take_health: a simple function which count pixels and return health
            self.enemy_health=self.take_health(enemy_health_ima)
       
    
    def take_health(self,image):
        #works only for  images on gray scale
        image=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        points=(image>128).sum() #yellow have a value bigger than 128
        health=points*100/np.prod(image.shape)
        return health
    
    def set_gamma(self,ga):
        self.gamma=ga

    def set_policy_net(self,net,logits=False):
        self.policy_net=net
        self.logits=logits

    def n_steps(self,n=1):
        rewards=0
        for i in range(n):
            if self.state is None:self.take_state()
            temp=np.expand_dims(cv2.cvtColor(self.state,cv2.COLOR_BGR2GRAY),axis=2)
            prob,_=self.policy_net(np.expand_dims(temp,axis=0).astype("float32"))
            if self.logits==True:prob=tf.nn.softmax(prob)
            prob=prob.numpy()[0]
            ind=np.random.choice(self.names_move,p=prob)
            action=self.names_move.index(ind)
            a=self.step(self.movements[ind])
            previous_state,self.state,rew,info=a
            if i==0:
                ini_state=previous_state
                ini_action=action
            rewards*=self.gamma
            rewards+=rew
            if self.state is None :
                return ini_state,self.state,rewards,info,ini_action
                
        return ini_state,self.state,rewards,info,ini_action


    def step(self,action):
        if self.state is None:self.take_state()#if image is None(that is, we have a new episode) restart the state
        previous_state=self.state
        healths=[self.health,self.enemy_health]
        key_do([32],frame_repeat=4)#continue game
        sleep(0.25)
        do_action(action)
        sleep(action[3])#waiting for the action completed(waiting time is specific for every action)
        key_do([32],frame_repeat=1)#pause the game
        self.take_state(infer=True)
        #we can add here the object detector
        healths.extend([self.health,self.enemy_health])#we will use it for calculating reward
        if (self.health<=0 or self.enemy_health<=0):
            key_do([32],frame_repeat=1)#continue the game
            while True:
               random_move=np.random.choice(self.names_move,1)[0]
               move=self.movements[random_move]
               do_action(move)
               sleep(0.5)
               self.take_state()
               if self.loss_win():break
               if (self.health==100 and self.enemy_health==100):break
            while True:
                key_do([32])#press enter
                sleep(0.2)
                self.take_state()
                if (self.health==100 and self.enemy_health==100):
                    sleep(3)
                    key_do([32])#pause the game
                    
                    break
            if self.wins==2 or self.loss==2:
                self.loss=0
                self.wins=0
            self.state=None
        reward,info=self.Calc_rew(healths)
        return previous_state,self.state,reward,info
                   
    def Calc_rew(self,healths):
        r=0.0
        info="None"
        if self.reward_end >0:info="win"
        if self.reward_end <0:info="loss"
        if self.reward_end:
            r+=(self.reward_end*100.0)
            self.reward_end=0
        r+=(healths[2]-healths[0])+2.0*(healths[1]-healths[3])
        
        return r,info

    def loss_win(self):
        if self.loss==0 and self.wins==0:
            prob1=self.end_net.predict(np.expand_dims(self.state[20:50,17:39,:],axis=0)).tolist()
            prob2=self.end_net.predict(np.expand_dims(self.state[20:50,466:488,:],axis=0)).tolist()
            if prob1[0][0]>0.5:
                self.wins+=1
                self.reward_end=1
                return True
            if prob2[0][0]>0.5:
                self.loss+=1
                self.reward_end=-1
                return True
        elif self.loss==1 and self.wins==0:
            prob1=self.end_net.predict(np.expand_dims(self.state[20:50,17:39,:],axis=0)).tolist()
            prob2=self.end_net.predict(np.expand_dims(self.state[20:50,443:465,:],axis=0)).tolist()
            if prob1[0][0]>0.5:
                self.wins+=1
                self.reward_end=1
                return True
            if prob2[0][0]>0.5:
                self.loss+=1
                self.reward_end=-1
                return True
        elif self.loss==0 and self.wins==1:
            prob1=self.end_net.predict(np.expand_dims(self.state[20:50,39:61,:],axis=0)).tolist()
            prob2=self.end_net.predict(np.expand_dims(self.state[20:50,466:488,:],axis=0)).tolist()
            if prob1[0][0]>0.5:
                self.wins+=1
                self.reward_end=1
                return True
            if prob2[0][0]>0.5:
                self.loss+=1
                self.reward_end=-1
                return True
        else:
            prob1=self.end_net.predict(np.expand_dims(self.state[20:50,39:61,:],axis=0)).tolist()
            prob2=self.end_net.predict(np.expand_dims(self.state[20:50,443:465,:],axis=0)).tolist()
            if prob1[0][0]>0.5:
                self.wins+=1
                self.reward_end=1
                return True
            if prob2[0][0]>0.5:
                self.loss+=1
                self.reward_end=-1
                return True
