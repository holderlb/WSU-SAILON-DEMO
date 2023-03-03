#!/usr/bin/env python3
# ************************************************************************************************ #
# **                                                                                            ** #
# **    AIQ-SAIL-ON Vizdoom GUI                                                                 ** #
# **                                                                                            ** #
# **        Brian L Thomas, 2020                                                                ** #
# **                                                                                            ** #
# **  Tools by the AI Lab - Artificial Intelligence Quotient (AIQ) in the School of Electrical  ** #
# **  Engineering and Computer Science at Washington State University.                          ** #
# **                                                                                            ** #
# **  Copyright Washington State University, 2020                                               ** #
# **  Copyright Brian L. Thomas, 2020                                                           ** #
# **                                                                                            ** #
# **  All rights reserved                                                                       ** #
# **  Modification, distribution, and sale of this work is prohibited without permission from   ** #
# **  Washington State University.                                                              ** #
# **                                                                                            ** #
# **  Contact: Vincent Lombardi (vincent.lombardi@wsu.edu)                                      ** #
# **  Contact: Larry Holder (holder@wsu.edu)                                                    ** #
# **  Contact: Diane J. Cook (djcook@wsu.edu)                                                   ** #
# ************************************************************************************************ #

import copy
import queue
import random
import sys
import threading
import cv2
import subprocess
import argparse


from objects.TA2_logic import TA2Logic


class ThreadedProcessingExample(threading.Thread):
    def __init__(self, processing_object: list, response_queue: queue.Queue):
        threading.Thread.__init__(self)
        self.processing_object = processing_object
        self.response_queue = response_queue
        self.is_done = False
        return

    def run(self):
        """All work tasks should happen or be called from within this function.
        """
        return

    def stop(self):
        self.is_done = True
        return


class TA2Agent(TA2Logic):
    def __init__(self, domain):
        super().__init__()

        if domain == 'vizdoom':
            print('controls a:left, d: right, w:forward, s:backward, j:shoot, k:turn left, l:turn right, q:QUIT, any other key: nothing')
            self.possible_answers = list()
            self.possible_answers.append(dict({'action': 'nothing'}))
            self.possible_answers.append(dict({'action': 'left'}))
            self.possible_answers.append(dict({'action': 'right'}))
            self.possible_answers.append(dict({'action': 'forward'}))
            self.possible_answers.append(dict({'action': 'backward'}))
            self.possible_answers.append(dict({'action': 'shoot'}))
            self.possible_answers.append(dict({'action': 'turn_left'}))
            self.possible_answers.append(dict({'action': 'turn_right'}))

            self.keycode = dict({113: 'q',
                                 119: 'w',
                                 97: 'a',
                                 115: 's',
                                 100: 'd',
                                 106: 'j',
                                 107: 'k',
                                 108: 'l'})

            self.key_action = dict({'a': 1,
                                    'd': 2,
                                    'w': 3,
                                    's': 4,
                                    'l': 7,
                                    'k': 6,
                                    'j': 5})
        elif domain == 'cartpole':
            print('controls a:left, d: right, w:forward, s:backward, q:QUIT, any other key: nothing')
            self.possible_answers = list()
            self.possible_answers.append(dict({'action': 'nothing'}))
            self.possible_answers.append(dict({'action': 'left'}))
            self.possible_answers.append(dict({'action': 'right'}))
            self.possible_answers.append(dict({'action': 'forward'}))
            self.possible_answers.append(dict({'action': 'backward'}))

            self.keycode = dict({113: 'q',
                                 119: 'w',
                                 97: 'a',
                                 115: 's',
                                 100: 'd'})

            self.key_action = dict({'a': 1,
                                    'd': 2,
                                    'w': 3,
                                    's': 4})

        # This variable can be set to true and the system will attempt to end training at the
        # completion of the current episode, or sooner if possible.
        self.end_training_early = False
        # This variable is checked only during the evaluation phase.  If set to True the system
        # will attempt to cleanly end the experiment at the conclusion of the current episode,
        # or sooner if possible.
        self.end_experiment_early = False
        return

    def user_interface(self, feature_vector: dict) -> dict:
        """Process an episode data instance.

        Parameters
        ----------
        feature_vector : dict
            The dictionary of the feature vector.  Domain specific feature vector formats are
            defined on the github (https://github.com/holderlb/WSU-SAILON-NG).

        Returns
        -------
        dict
            A dictionary of your label prediction of the format {'action': label}.  This is
                strictly enforced and the incorrect format will result in an exception being thrown.
        """
        found_error = False
        image = feature_vector['image']
        if image is None:
            self.log.error('No image received. Did you set use_image to True in TA1.config '
                           'for vizdoom?')
            found_error = True

        # If we found an error, we need to exit.
        if found_error:
            self.log.error('Closing Program')
            stop_generator()
            sys.exit()

        s = 640.0 / image.shape[1]
        dim = (640, int(image.shape[0] * s))

        resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

        cv2.imshow('Generator', resized)
        keycode = cv2.waitKey(int(10 * 1000))
        key_pressed = ' '
        if int(keycode) in self.keycode:
            key_pressed = self.keycode[int(keycode)]
        self.log.debug('keycode: {}   {}'.format(keycode, key_pressed))

        if key_pressed == 'q':
            stop_generator()
            sys.exit()

        act = 0
        if key_pressed in self.key_action:
            act = self.key_action[key_pressed]

        label_prediction = self.possible_answers[act]

        return label_prediction

    def experiment_start(self):
        pass

    def training_start(self):
        pass

    def training_episode_start(self, episode_number: int):
        pass

    def training_instance(self, feature_vector: dict, feature_label: dict) -> dict:
        """Process a training

        Parameters
        ----------
        feature_vector : dict
            The dictionary of the feature vector.  Domain specific feature vector formats are
            defined on the github (https://github.com/holderlb/WSU-SAILON-NG).
        feature_label : dict
            The dictionary of the label for this feature vector.  Domain specific feature labels
            are defined on the github (https://github.com/holderlb/WSU-SAILON-NG). This will always
            be in the format of {'action': label}.  Some domains that do not need an 'oracle' label
            on training data will receive a valid action chosen at random.

        Returns
        -------
        dict
            A dictionary of your label prediction of the format {'action': label}.  This is
                strictly enforced and the incorrect format will result in an exception being thrown.
        """

        feature_debug = copy.deepcopy(feature_vector)
        feature_debug['image'] = list()
        self.log.debug('Training Instance: feature_vector={}  feature_label={}'.format(
            feature_debug, feature_label))

        label_prediction = self.user_interface(feature_vector=feature_vector)

        return label_prediction

    def training_performance(self, performance: float, feedback: dict = None):
        pass

    def training_episode_end(self, performance: float, feedback: dict = None) -> \
            (float, float, int, dict):
        """Provides the final performance on the training episode and indicates that the training
        episode has ended.

        Parameters
        ----------
        performance : float
            The final normalized performance score of the episode.
        feedback : dict, optional
            A dictionary that may provide additional feedback on your prediction based on the
            budget set in the TA1. If there is no feedback, the object will be None.

        Returns
        -------
        float, float, int, dict
            A float of the probability of there being novelty.
            A float of the probability threshold for this to evaluate as novelty detected.
            Integer representing the predicted novelty level.
            A JSON-valid dict characterizing the novelty.
        """
        self.log.info('Training Episode End: performance={}'.format(performance))

        novelty_probability = random.random()
        novelty_threshold = 0.8
        novelty = 0
        novelty_characterization = dict()

        return novelty_probability, novelty_threshold, novelty, novelty_characterization

    def training_end(self):
        pass

    def train_model(self):
        pass

    def save_model(self, filename: str):
        pass

    def reset_model(self, filename: str):
        pass

    def trial_start(self, trial_number: int, novelty_description: dict):
        pass

    def testing_start(self):
        pass

    def testing_episode_start(self, episode_number: int):
        pass

    def testing_instance(self, feature_vector: dict, novelty_indicator: bool = None) -> dict:
        """Evaluate a testing instance.  Returns the predicted label or action, if you believe
        this episode is novel, and what novelty level you beleive it to be.

        Parameters
        ----------
        feature_vector : dict
            The dictionary containing the feature vector.  Domain specific feature vectors are
            defined on the github (https://github.com/holderlb/WSU-SAILON-NG).
        novelty_indicator : bool, optional
            An indicator about the "big red button".
                - True == novelty has been introduced.
                - False == novelty has not been introduced.
                - None == no information about novelty is being provided.

        Returns
        -------
        dict
            A dictionary of your label prediction of the format {'action': label}.  This is
                strictly enforced and the incorrect format will result in an exception being thrown.
        """
        feature_debug = copy.deepcopy(feature_vector)
        feature_debug['image'] = list()
        self.log.debug('Testing Instance: feature_vector={}, novelty_indicator={}'.format(
            feature_debug, novelty_indicator))

        label_prediction = self.user_interface(feature_vector=feature_vector)

        return label_prediction

    def testing_performance(self, performance: float, feedback: dict = None):
        pass

    def testing_episode_end(self, performance: float, feedback: dict = None) -> \
            (float, float, int, dict):
        """Provides the final performance on the testing episode.

        Parameters
        ----------
        performance : float
            The final normalized performance score of the episode.
        feedback : dict, optional
            A dictionary that may provide additional feedback on your prediction based on the
            budget set in the TA1. If there is no feedback, the object will be None.

        Returns
        -------
        float, float, int, dict
            A float of the probability of there being novelty.
            A float of the probability threshold for this to evaluate as novelty detected.
            Integer representing the predicted novelty level.
            A JSON-valid dict characterizing the novelty.
        """
        self.log.info('Testing Episode End: performance={}'.format(performance))

        novelty_probability = random.random()
        novelty_threshold = 0.8
        novelty = random.choice(list(range(4)))
        novelty_characterization = dict()

        return novelty_probability, novelty_threshold, novelty, novelty_characterization

    def testing_end(self):
        pass

    def trial_end(self):
        pass

    def experiment_end(self):
        pass


def enter_sudo():
    cmd_str = 'sudo echo "Running generator!"'
    subprocess.run(cmd_str, shell=True)
    return


def start_generator():
    cmd_str = "sudo docker-compose -f generator/portable-gui.yml up -d"
    subprocess.run(cmd_str, shell=True)
    return


def stop_generator():
    cmd_str = "sudo docker-compose -f generator/portable-gui.yml down"
    subprocess.run(cmd_str, shell=True)
    return


if __name__ == "__main__":
    # Handle command line args
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain', default='vizdoom')
    args = parser.parse_args()



    domain = args.domain



    # Select correct config
    config_name = None
    if domain == 'vizdoom':
        config_name = '--config=generator/configs/partial/gui-vizdoom.config'
    elif domain == 'cartpole':
        config_name = '--config=generator/configs/partial/gui-cartpole.config'

    # Set params for future arg parser
    sys.argv = sys.argv[0:1] + [config_name, '--printout', '--ignore-secret']

    print(sys.argv)

    # Get thread sudo permissions for docker-compose
    enter_sudo()

    x = threading.Thread(target=start_generator, args=())
    x.start()

    agent = TA2Agent(domain)
    agent.run()
