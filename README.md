# Street fighter II BOT based on Enviroment with Image Screenshot



# DESCRIPTION
Here I tried to train a bot for street fighter with the help of a screencapture environment.

In summary, a simulator run the game and by captyring the image of the game, we derive the informations that we need for training the Network.  Inference of health is done by counting the pixels of health-bar or we can use a network for more complex situations. It should be mentioned that many times the game does not end when healths go to zero so another approach used for finished episodes. For winning a champion and move to the next map,we must win two round-wins and every time we win ,a hand is appeared next to the health bar of the player and so on I trained a small network to detect if there are hands..

