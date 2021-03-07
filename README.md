# Street fighter II BOT based on Enviroment with Image Screenshot



# DESCRIPTION
Here I tried to train a bot for street fighter with the help of a screencapture environment.

In summary, a simulator runs the game and by captyring the image of the game, we derive the informations that we need for training the Network.  Inference of health is done by counting the pixels of health-bar or we may use a network for more complex situations. It should be mentioned that many times the game does not end when healths go to zero so another approach used for finished episodes. For winning a champion and move to the next map,we must win two round-wins and every time we win ,a hand is appeared next to the health bar of the player and so on I trained a small network to detect if there are hands..

-- Game should be opened in prefixed position and size

-- Coordinates(x,y,w,h) for image screenshot is different for every user

-- Network that detect Wins-Losses is trained on RGB images,thats why images are not in gray scale from the beginning of the code

# Implementation and Theory:

- #### Maths 

The Reinforcement Algorithm that we use is A2C(Advantage-Actor-Critic). Actor and Critic networks share the same parameters and the update is done according to the losses:

![image](https://user-images.githubusercontent.com/70138386/110235119-1c520c00-7f37-11eb-9a82-d64202dc19ef.png)


![image](https://user-images.githubusercontent.com/70138386/110207454-3c78c100-7e8c-11eb-9652-64e483215845.png)


A Entropy loss have been added in the policy loss,in purpose to push the Policy to a more uniform distribution(Entropy has a minimum for the uniform distribution).

- #### Network

This Network layout is not the best choice so improvements can be made but there is no need for deep Networks(may 3-4 Conv layers can do the job)

![image](https://user-images.githubusercontent.com/70138386/110235317-127cd880-7f38-11eb-8fe8-e4e0164429ff.png)

- #### Environment

Implementation of  environment is based on 'personal' details,that is the ***Coordinates*** of the informations we infer are **Specific** for my computer and they depend from the *position* and *size* of simulator's window. So if you want to use the module,you need to make adjustments.

![image](https://user-images.githubusercontent.com/70138386/110235880-52918a80-7f3b-11eb-934f-a9a652217f12.png)


