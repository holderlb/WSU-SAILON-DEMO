from .p_base import CartPoleBulletEnv
import os
import sys
import random
import pybullet as p2
import numpy as np
from pybullet_utils import bullet_client as bc


class CartPole(CartPoleBulletEnv):

    def __init__(self, difficulty, params: dict = None):
        super().__init__(params=params)

        self.difficulty = difficulty
        self.file_name = 'cartpole.urdf'

        return None

    # Used to generate the initial world state
    def generate_world(self):
        # Create bullet physics client
        if self._renders:
            self._p = bc.BulletClient(connection_mode=p2.GUI)
        else:
            self._p = bc.BulletClient(connection_mode=p2.DIRECT)
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K") # Clear to the end of line

        # Client id link, for closing or checking if running
        self._physics_client_id = self._p._client

        # Load world simulation
        p = self._p
        p.resetSimulation()
        p.setGravity(0, 0, -9.8)
        p.setTimeStep(self.timeStep)
        p.setRealTimeSimulation(0)

        # Load world objects
        self.cartpole = p.loadURDF(os.path.join(self.path, 'models', 'ground_cart.urdf'))
        self.walls = p.loadURDF(os.path.join(self.path, 'models', 'walls.urdf'))
        self.origin = p.loadURDF(os.path.join(self.path, 'models', 'origin.urdf'))

        # Set walls to be bouncy
        for joint_nb in range(-1, 6):
            p.changeDynamics(self.walls, joint_nb, restitution=1.0, lateralFriction=0.0,
                             rollingFriction=0.0, spinningFriction=0.0)

        return None

    def reset_world(self):
        # Reset world (assume is created)
        p = self._p

        # Delete cartpole
        if self.cartpole == -10:
            self.cartpole = p.loadURDF(os.path.join(self.path, 'models/p/', self.file_name))
        else:
            p.removeBody(self.cartpole)
            self.cartpole = p.loadURDF(os.path.join(self.path, 'models/p/', self.file_name))

        # Set cart to have no friction
        p.changeDynamics(self.cartpole, -1, linearDamping=0, angularDamping=0)
        p.changeDynamics(self.cartpole, 0, linearDamping=0, angularDamping=0)
        p.changeDynamics(self.cartpole, 1, linearDamping=0, angularDamping=0)

        # Set pole to loose
        p.setJointMotorControl2(self.cartpole, 1, p.VELOCITY_CONTROL, force=0)
        p.setJointMotorControl2(self.cartpole, 0, p.VELOCITY_CONTROL, force=0)

        # Set random initial state
        randstate = self.np_random.uniform(low=-0.01, high=0.01, size=(2,))
        p.resetJointState(self.cartpole, 0, randstate[0], 1.0)
        p.resetJointState(self.cartpole, 1, 0.0, 0.4)
        self.state = p.getJointState(self.cartpole, 1)[0:2] + p.getJointState(self.cartpole, 0)[0:2]


        # Load blocks in
        self.nb_blocks = random.randint(0, 2) + 2
        self.blocks = [None] * self.nb_blocks
        for i in range(self.nb_blocks):
            self.blocks[i] = p.loadURDF(os.path.join(self.path, 'models', 'block.urdf'))

        # Set blocks to be bouncy
        for i in self.blocks:
            p.changeDynamics(i, -1, restitution=1.0, lateralFriction=0.0,
                             rollingFriction=0.0, spinningFriction=0.0)

        # Set block posistions
        min_dist = 1
        cart_pos, _ = p.getBasePositionAndOrientation(self.cartpole)
        cart_pos = np.asarray(cart_pos)
        for i in self.blocks:
            pos = self.np_random.uniform(low=-4.0, high=4.0, size=(3,))
            pos[2] = pos[2] + 5.0
            while np.linalg.norm(cart_pos[0:2] - pos[0:2]) < min_dist:
                pos = self.np_random.uniform(low=-4.0, high=4.0, size=(3,))
                # Z is not centered at 0.0
                pos[2] = pos[2] + 5.0
            p.resetBasePositionAndOrientation(i, pos, [0, 0, 1, 0])

        # Set block velocities
        for i in self.blocks:
            vel = self.np_random.uniform(low=6.0, high=10.0, size=(3,))
            for ind, val in enumerate(vel):
                if random.random() < 0.5:
                    vel[ind] = val * -1

            p.resetBaseVelocity(i, vel, [0, 0, 0])

        return None