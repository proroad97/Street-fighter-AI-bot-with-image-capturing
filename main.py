import tensorflow as tf
import numpy as np
import cv2
from time import sleep
import Enviroment as Env
import Network as net
import pyautogui
"""
--Game's window should be opened in prefixed position and size every time(you can use winSize2 script)
--Also find the correct coordinates for "mouse-clicking" that we need for opening the game
--It had been trained only for RUY who is the easiest player to learn
--Color channel is changed(in Gray scale) here because Environment needs Colored images for infering healths but network had be trained on gray images

"""
movements={
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

names_mov=list(movements.keys())

coord=(8,95,512,475)#coordinates are different for every user...
env=Env.Enviroment(coord)
state=env.start_game(Open=True)
env.set_gamma(0.95)
Net=net.ActorCritic(state.shape,len(movements))
env.set_policy_net(Net)
file=r"\training_1\cp.ckpt"



def make_batches(env,batch=32,steps=1,gamma=0.95):
    """ 
    Make batches of n_steps(bootstrapping)

    Network expects float and Gray images, so we convert them

    Returns: Initial_state,rewards,next_state,index of finished episodes,actions
    """
    states=[]
    rewards=[]
    next_states=[]
    actions=[]
    dones_idx=[]

    for i in range(batch):
        state,next_state,reward,info,action=env.n_steps(steps)
        #cv2 returns an image's shape of (h,w) in Gray scale and so it should be added the gray channel
        states.append(np.expand_dims(cv2.cvtColor(state,cv2.COLOR_BGR2GRAY),axis=2))
        rewards.append(reward)
        if next_state is not None:
            next_states.append(np.expand_dims(cv2.cvtColor(next_state,cv2.COLOR_BGR2GRAY),axis=2))
            dones_idx.append(i)
        actions.append(action)   
    rewards=np.array(rewards)    
    next_states=np.array(next_states).astype("float32")
    _,last_values=Net(next_states)
    ref_rewards=rewards[dones_idx]+(gamma**steps)*(last_values.numpy().squeeze())
    return np.array(states).astype("float32"),rewards,next_states,dones_idx,np.array(actions)

opti=tf.optimizers.Adam(learning_rate=1e-7)
model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(filepath=file,save_weights_only=True,monitor="loss")
Net.compile(optimizer=opti,loss=[net.policy_loss,'mse'],run_eagerly=True)#Custom loss work only in Eager mode

def train(epoch=1,batch=8,steps=1):
    rewards=[]
    losses=0
    total_wins=0
    for i in range(epoch):
        wind=pyautogui.getWindowsWithTitle("snes9x")[0]
        if i%5==0:
            #activation of the computer every 5 iterations
            try:
                wind.activate()
            except:
                pass
        states,cum_rewards,next_states,dones,actions=make_batches(env,batch=batch,steps=1,gamma=0.95)
        rewards.append(cum_rewards.sum()/8)
        if (cum_rewards.sum()/8)>30:
            print("i breaked in epoch: {}".format(i))
            break
        print("total reward per episode : {}".format(rewards[i]),"\n epoch:",i )
        _,values=Net(states)
        values=values.numpy().squeeze()
        adva=cum_rewards-values
        combined=tf.stack((adva,actions),axis=1)
        Net.fit(states,[combined,cum_rewards],epochs=1,callbacks=model_checkpoint_callback)
        
        
def play():
    try:
        wind=pyautogui.getWindowsWithTitle("snes9x")[0]
        wind.activate()
    except:
        pass
    while True:
        env.take_state(infer=False)
        state=(env.state).astype("float32")
        state=np.expand_dims(np.expand_dims(cv2.cvtColor(state,cv2.COLOR_BGR2GRAY),axis=2),axis=0)
        Prob,_=Net(state)
        act=np.argmax(Prob.numpy()[0])
        action=names_mov[act]
        _,_,_,info=env.step(movements[action],pause=False)
        if info !="None":break

        
        
train(epoch=20000,batch=6,steps=1)
#play()
