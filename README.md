# Street fighter II BOT based on Enviroment with Image Screenshot



# DESCRIPTION
Here I tried to train a bot for street fighter with the help of a screencapture environment.

In summary, a simulator run the game and by captyring the image of the game, we derive the informations that we need for training the Network.  Inference of health is done by counting the pixels of health-bar or we can use a network for more complex situations. It should be mentioned that many times the game does not end when healths go to zero so another approach used for finished episodes. For winning a champion and move to the next map,we must win two round-wins and every time we win ,a hand is appeared next to the health bar of the player and so on I trained a small network to detect if there are hands..

-- Game should be opened in prefixed position and size

-- Coordinates(x,y,w,h) for image screenshot is different for every user

-- Network that detect Wins-Losses is trained on RGB images,thats why images are not in gray scale from the beginning of the code

# Implementation and Theory

The Reinforcement Algorithm that we use is A2C(Advantage-Actor-Critic). Actor and Critic networks share the same parameters and the update is done according to the losses:

![image](https://user-images.githubusercontent.com/70138386/110207344-8319eb80-7e8b-11eb-870e-b3b2778050df.png) 


![image](https://user-images.githubusercontent.com/70138386/110207353-9331cb00-7e8b-11eb-868e-6db99bbce030.png)


![image](https://user-images.githubusercontent.com/70138386/110207454-3c78c100-7e8c-11eb-9652-64e483215845.png)
