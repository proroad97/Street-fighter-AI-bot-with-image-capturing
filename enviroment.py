import tensorflow as tf
import numpy as np
from PIL import ImageGrab
import copy
import pyautogui
import cv2
import subprocess



class Enviroment():
    def __init__(path):
        self.start_game()
        self.end_net=tf.keras.models.load_model(os.path.normcase(path["end_network"]))#maybe a network that will understand if the player lost or win
        self.det_net=tf.keras.models.load_model(....)#the network of object detection

    def start_game(self,*coord):
        """ open the game,initialize stats and capture the "state"(take screenshot)"""
        self.wins=0
        self.loss=0
        self.health=100
        self.enemy_health=100
        self.done=False
        self.Open_game()
        self.wind=pyautogui.getWindowsWithTitle("snes9x")[0]#Find the window of the game
        self.wind.activate()#It is like we left click on the game's window,so this window become the active. With that way it is achieved sending input in the game
        self.state=np.array(ImageGrab.grab(coord))#In my PC: x=8,y=95,w=512,h=475.change them with your coordinates
    
    def Open_game(self):
        """ 
        open the game and do the rights "clicks" and press the right "buttons"
        to select the player and pause the game exactly at 99 remaing time
        
        Again you should pick the correct coordinates for mouse
        """
        os.chdir(r"C:\Users\PROROAD\Desktop")#put your game's directory
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



    def take_state(self):
        """we should find the coordinates of the health bar. Or with hard-code or a object detector"""
        self.image_boundarys=()
        self.state=np.array(ImageGrab.grab(self.image_boundarys))
        health_ima= cv2.cvtColor(state[:,:,:],cv2.COLOR_RGB2BGR)#taking the image with health and transform it on BGR
        enemy_health_ima=cv2.cvtColor(state[:,:,:],cv2.COLOR_RGB2BGR)
        self.health=take_health(health_ima)#take_health: a simple function which count pixels or a dense model
        self.enemy_health=take_health(enemy_health_ima)
        if( self.health<=0 or  self.enemy_health<0):
            done=loss_state(state)
            self.done=done

    def step(self,action):
        previous_state=self.state
        prev_health=[self.health,self.enemy_health]
        #continue the game
        #do an action
        # wait for 0.5-1 sec

    def key_do(keys, frame_repeat=2):
        for key in keys:
            win32api.keybd_event(key,0,0,0)
        sleep(frame_repeat*0.25)
        for key in keys:
            win32api.keybd_event(key,0,win32con.KEYEVENTF_KEYUP,0)

   
    def loss_win(self,state):
        """maybe a function that will infer if the player lost or win(some times the health zeroed but the game have not ended)"""
        image=state[:,:,:]
        stats=end_net(image)
        if stats==0:return False
        elif stats==1: self.wins=+1
        else: self.loss+=1
        return True
    
    def reset(self):
