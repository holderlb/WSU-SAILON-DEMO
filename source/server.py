#!/usr/bin/python
import ast
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
