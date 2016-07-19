import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from collections import defaultdict
from collections import Counter


def multi_dimensions(n, type):
  """ Creates an n-dimension dictionary where the n-th dimension is of type 'type'
  """
  if n<=1:
    return type()
  return defaultdict(lambda:multi_dimensions(n-1, type))

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.alpha=0.9
        self.gamma=0.9
        self.Q=multi_dimensions(2, Counter)
        self.actions=Environment.valid_actions
        self.num_moves=0
        self.reach_dest=0
        self.current_trial=0
        self.penalty = 0






    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required


    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (self.next_waypoint, inputs['light'], inputs['oncoming'],inputs['left'])
        #print(self.state)

        # TODO: Select action according to your policy

        self.epsilon=1/float(t+self.current_trial+1)
        #proposed_action=random.choice(Environment.valid_actions)
        self.Q[self.state][self.state[0]]=self.Q[self.state][self.state[0]]+0.1
        Q_actions=[]
        #Implementation of epsilon-greedy exploration vs explotation
        if random.random() < self.epsilon:
            proposed_action = random.choice(self.actions)
            maxQ = self.Q[self.state][proposed_action]
        else:
            maxQ = max(self.Q[self.state][next_action] for next_action in self.actions)
        for next_action in self.actions:
            Q_actions.append(self.Q[self.state][next_action])
            if (self.Q[self.state][next_action]==maxQ):
                proposed_action=next_action
                #print("Q learing works",proposed_action)
        #print (random.random(),self.epsilon)



        action=proposed_action
        reward = self.env.act(self, action)
        next_state = (self.next_waypoint, inputs['light'], inputs['oncoming'], inputs['left'])
        # TODO: Learn policy based on state, action, reward
        #Learning policy implemented by recording the Q value to Q matrix for particular state
        self.Q[self.state][action] = (1.0 - self.alpha) * self.Q[self.state][action] + self.alpha * (
        reward + self.gamma * max(self.Q[next_state][next_action] for next_action in self.actions))

        # Statistics
        self.num_moves += 1
        add_total = False
        if reward < 0:  # Assign penalty if reward is negative
            self.penalty += 1
            add_total = False
        if deadline == 0:
            add_total = True
        if reward >= 10:  # agent has reached destination
            self.reach_dest += 1
            add_total = True
        if add_total:
            self.current_trial += 1
        if self.current_trial>0: success_rate =  "{}/{} = %{}".format(self.reach_dest, self.current_trial,
                                            (round(float(self.reach_dest) / float(self.current_trial), 3)) * 100)
        else:
            success_rate = "{}/{} = %{}".format(0, 0, 0)
        if self.num_moves > 0:  penalty_ratio = "{}/{} = %{}".format(self.penalty, self.num_moves,
                                             (round(float(self.penalty) / float(self.num_moves), 4)) * 100)
        else:
            penalty_ratio = "{}/{} = %{}".format(0,0,0)
        if (t==0): print(success_rate, penalty_ratio)

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs,
                                                                                                    action,
                                                                                                    reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=1.0)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit





if __name__ == '__main__':
    run()
