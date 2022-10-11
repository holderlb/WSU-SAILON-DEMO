#!/usr/bin/python
import sys
import ast
import time
import json
import socket
import pickle
import docker
import argparse


import numpy as np
import statistics


class User:

    def __init__(self, host, port, domain, novel, seed):
        pygame.init()
        pygame.font.init()
        self.domain = domain
        self.novel = novel
        self.seed = seed
        self.my_font = pygame.font.SysFont('Comic Sans MS', 30)
        self.display = pygame.display.set_mode((640, 480))
        self.socket = None

        if self.novel:
            self.novel = 110
        else:
            self.novel = 200

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.connect((host, port))
            self.run()

        return

    def run(self):
        # Send initial game setting
        data = json.dumps({'command': 'reset', 'domain': self.domain, 'novelty_level': self.novel,
                           'difficulty': 'easy', 'seed': self.seed})
        print(data)
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
        if self.domain == 'vizdoom':
            text_surface = [self.my_font.render('W, A, S, D: Move', False, (255, 255, 255)),
                            self.my_font.render('Q, E: Turn', False, (255, 255, 255)),
                            self.my_font.render('SPACE: Shoot', False, (255, 255, 255))]
            self.display.blit(surf, (0, 0))
            self.display.blit(text_surface[0], (0, 0))
            self.display.blit(text_surface[1], (0, 30))
            self.display.blit(text_surface[2], (0, 60))
        else:
            text_surface = [self.my_font.render('A, D: Move', False, (0, 0, 0))]
            self.display.blit(surf, (0, 0))
            self.display.blit(text_surface[0], (0, 0))
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
                    if self.domain == 'cartpole':
                        if event.key == pygame.K_a:
                            action = 'right'
                        if event.key == pygame.K_d:
                            action = 'left'
            if action is not None:
                return {'action': action}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', default='user')
    parser.add_argument('-r', '--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default='55555')
    parser.add_argument('-d', '--domain', default='vizdoom')
    parser.add_argument('-n', '--novel', action='store_true')
    parser.add_argument('-s', '--seed', default=None)
    args = parser.parse_args()

    # Load in parameters
    vers = args.version
    host = args.host
    port = int(args.port)
    domain = args.domain
    novel = args.novel
    seed = args.seed

    if vers not in ['user', 'dock']:
        print('Can only user or docker!')
        exit()
    if domain not in ['cartpole', 'vizdoom']:
        print('Can only run vizdoom or cartpole!')
        exit()

    # python visual.py "user" "vizdoom" "base" "127.0.0.1" "55555"
    if vers == 'user':
        ports = {port: port}
        env = {'VERS': 'dock',
               'HOST': '0.0.0.0',
               'PORT': str(port)}
        #client = docker.from_env()
        #container = client.containers.run("wsudemo:latest", environment=env, ports=ports, detach=True)
        import pygame
        from pygame.locals import *
        user_game = User(host, port, domain, novel, seed)
    elif vers == 'dock':
        dock_game = Dock(host, port)
