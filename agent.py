import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.gamma=0.5
        self.Q=[[0 for j in range(6)] for i in range(8)]


    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        # 2-dimension array Q have used to save Q values for each state
        self.Q= [[0 for j in range(6)] for i in range(8)]


    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = inputs['location']
        self.heading=inputs['heading']

        # TODO: Select action according to your policy
        # Extract Q of possible actions: forward, left and right
        #In case of possible action is out of borders, make it equal -100
        x_forw=self.state[0]+self.heading[0]-1
        y_forw=self.state[1]+self.heading[1]-1
        if (x_forw>=0 and x_forw<=7) and (y_forw>=0 and y_forw<=5):
            Q_forward=self.Q[x_forw][y_forw]
        else: Q_forward=-100

        x_left=self.state[0] +self.heading[1]-1
        y_left=self.state[1] -self.heading[0]-1
        if (x_left>=0 and x_left<=7) and (y_left>=0 and y_left<=5):
            Q_left = self.Q[x_left][y_left]
        else: Q_left=-100

        x_right=self.state[0]-self.heading[1]-1
        y_right=self.state[1]+ self.heading[0]-1
        if (x_right>=0 and x_right<=7) and (y_right>=0 and y_right<=5):
            Q_right = self.Q[x_right][y_right]
        else: Q_right=-100

        #Make actions of stop on the crossroad not very utile
        Q_none=-1

        #Increase Q +1 in case of action suggested by planner
        #In case of prohibited by traffic rules action makes Q=-100
        if self.next_waypoint == 'right':
            Q_right=Q_right+1
            if inputs['light'] == 'red' and inputs['left'] == 'forward':
                Q_right=-100
        elif self.next_waypoint == 'forward':
            Q_forward = Q_forward+1
            if inputs['light'] == 'red':
                Q_forward=-100
        elif self.next_waypoint == 'left':
            Q_left = Q_left+1
            if inputs['light'] == 'red' or (inputs['oncoming'] == 'forward' or inputs['oncoming'] == 'right'):
                Q_left=-100
        #action = None

        # Execute action the best action by Q and get reward
        if (Q_forward>=Q_left) and (Q_forward>=Q_right) and (Q_forward>=Q_none):
            self.next_waypoint='forward'
            Q_action=Q_forward
        elif (Q_left>=Q_forward) and (Q_left>=Q_right) and (Q_left>=Q_none):
            self.next_waypoint = 'left'
            Q_action = Q_left
        elif (Q_right >= Q_forward) and (Q_right >= Q_left) and (Q_right >= Q_none):
            self.next_waypoint = 'right'
            Q_action = Q_right

        action = self.next_waypoint
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        #Learning policy implemented by recording the Q value to Q matrix for particular state
        self.Q[self.state[0]-1][self.state[1]-1]=reward+self.gamma*Q_action
        #print self.Q
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=False)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=1.0)  # reduce update_delay to speed up simulation
    sim.run(n_trials=10)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
