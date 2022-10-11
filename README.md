# Installation
* Requirments:
  * [docker](https://docs.docker.com/engine/install/ubuntu/)
  * python 3.6
    * Numpy
    * PyGame
    * [python docker api](https://docker-py.readthedocs.io/en/stable/)
    
# Building
The docker file must be built before running. To do so run the following command:
```
docker build -f Dockerfile-VISUAL -t wsudemo .
```
The build process will take several minutes.
    
# Running
To run the visual demo enter the following command:
```
python visual.py
```

### Options
* ``--domain <val>`` {cartpole, vizdoom}, defualts to vizdoom.
* ``--novel`` Enable novelty, defaults to false. 
* ``--seed <val>`` {int} Used to set the seed, defaults to random seed.

Example:
```
python visual.py --novel --seed 123 --domain vizdoom
```

## Playing
To play select the pygame window and press the key correpsonding to the desired action. 
One key press per action and frame update.

# Notes
* The doom game engine is a frame late for updating ammo used. Shoot commands act imediatly and the ammo graphic will be updated next tick.
* If you cannot use docker on your system due to privlage issues, the dockerfile contains the installation instructions. 
# Debug
### Port in use
If the default port 55555 is already in use, another port can be specified with: ```--port <val>```. 

Similary with host: ```--host <val>``` like 127.0.0.10.
 
### Port stuck open
If you find a port communication bug try waiting for a minute.

If it is still an issue the docker might still be running. To kill it type:
```
docker ps
```
Find the ID of the latst container then enter:
```
docker kill <id>
```