#!/usr/bin/python
import sys
import time
import json
import socket
import pickle
import docker
import argparse

import numpy as np
import statistics


class Dock:

    def __init__(self, host, port):
        self.HOST = host  # Standard loopback interface address (localhost)
        self.PORT = port  # Port to listen on (non-privileged ports are > 1023)
        self.conn = None
        self.env = None

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen()
            self.conn, addr = s.accept()
            with self.conn:
                self.listen()
        return

    def listen(self):
        while True:
            data = self.conn.recv(1024)
            if not data:
                break
            # Convert to json
            data = json.loads(data.decode("utf-8"))

            # Filter command
            if data['command'] == 'reset':
                self.reset(data['domain'], data['novelty_level'], data['difficulty'], data['seed'])
            if data['command'] == 'act':
                self.act({'action': data['action']})
            if data['command'] == 'exit':
                return

            # Send state
            state = json.dumps({'is_done': self.env.is_episode_done(),
                                'performance': self.env.information['performance']})
            self.conn.sendall(bytes(state, encoding="utf-8"))

            # Send image
            if self.env.is_episode_done():
                break
            else:
                self.conn.sendall(self.get_image())

        return

    def reset(self, domain, novelty, difficulty, seed):
        from partial_env_generator.phase_3.test_handler import TestHandler
        path = "partial_env_generator/phase_3/envs/"
        self.env = None
        self.env = TestHandler(domain=domain, novelty=novelty, trial_novelty=novelty,
                               difficulty=difficulty, seed=seed, use_img=True, path=path,
                               use_gui=False, ta2_generator_config={'start_zeroed_out': False})

        return

    def act(self, action):
        performance = self.env.apply_action(action)
        return performance

    def get_image(self):
        img = self.env.test.env.get_image()
        return img.tobytes()


class User:

    def __init__(self, host, port, domain, novel):
        pygame.init()
        pygame.font.init()
        self.domain = domain
        self.novel = novel
        self.my_font = pygame.font.SysFont('Comic Sans MS', 30)
        self.display = pygame.display.set_mode((640, 480))
        self.socket = None

        if self.novel == 'base':
            self.novel = 200
        else:
            self.novel = 110

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.connect((host, port))
            self.run()

        return

    def run(self):
        # Send initial game setting
        data = json.dumps({'command': 'reset', 'domain': self.domain, 'novelty_level': self.novel,
                           'difficulty': 'easy', 'seed': 123})
        self.socket.sendall(bytes(data, encoding="utf-8"))

        while True:
            # Get state
            state_data = self.socket.recv(1024)
            state = json.loads(state_data.decode("utf-8"))
            # Check for done
            if state['is_done']:
                break

            # Get screen
            game_screen = np.reshape(np.frombuffer(self.recvall(), dtype=np.uint8), (480, 640, 3))
            self.draw_game(game_screen)

            # Get user input
            action = self.get_input()

            # Send action command
            command = json.dumps({'command': 'act', 'action': action['action']})
            self.socket.sendall(bytes(command, encoding="utf-8"))

        print('Final Performance', state['performance'])

        # Close game
        pygame.display.quit()
        pygame.quit()

        return

    def recvall(self):
        BUFF_SIZE = 1024 # 4 KiB
        data = b''
        while True:
            part = self.socket.recv(BUFF_SIZE)
            data += part
            if len(data) == 640 * 480 * 3:
                # either 0 or end of data
                break
        return data

    def draw_game(self, game_screen):
        surf = pygame.surfarray.make_surface(np.flipud(np.rot90(game_screen)))
        text_surface = [self.my_font.render('W, A, S, D: Move', False, (255, 255, 255)),
                        self.my_font.render('Q, E: Turn', False, (255, 255, 255)),
                        self.my_font.render('SPACE: Shoot', False, (255, 255, 255))]
        self.display.blit(surf, (0, 0))
        self.display.blit(text_surface[0], (0, 0))
        self.display.blit(text_surface[1], (0, 30))
        self.display.blit(text_surface[2], (0, 60))
        pygame.display.update()

        return

    def get_input(self):
        while True:
            action = None
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if self.domain == 'vizdoom':
                        if event.key == pygame.K_w:
                            action = 'forward'
                        if event.key == pygame.K_s:
                            action = 'backward'
                        if event.key == pygame.K_a:
                            action = 'left'
                        if event.key == pygame.K_d:
                            action = 'right'
                        if event.key == pygame.K_q:
                            action = 'turn_left'
                        if event.key == pygame.K_e:
                            action = 'turn_right'
                        if event.key == pygame.K_SPACE:
                            action = 'shoot'
            if action is not None:
                return {'action': action}


if __name__ == "__main__":
    # Load in parameters
    vers = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])

    domain = "vizdoom"
    novel = "base"

    if vers not in ['user', 'dock']:
        print('Can only user or docker!')
        exit()
    if domain not in ['cartople', 'vizdoom']:
        print('Can only run vizdoom or cartpole!')
        exit()
    if novel not in ['base', 'novel']:
        print('Can only run base or novel!')
        exit()

    # python visual.py "user" "vizdoom" "base" "127.0.0.1" "55555"
    if vers == 'user':
        ports = {port: port}
        env = {'VERS': 'dock',
               'HOST': '0.0.0.0',
               'PORT': str(port)}
        client = docker.from_env()
        container = client.containers.run("wsudemo:latest", environment=env, ports=ports, detach=True)
        import pygame
        from pygame.locals import *
        user_game = User(host, port, domain, novel)
    elif vers == 'dock':
        dock_game = Dock(host, port)
