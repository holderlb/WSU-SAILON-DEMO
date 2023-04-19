# Installation
* Requirements:
  * Ubuntu 22.04 LTS
  * [docker](https://docs.docker.com/engine/install/ubuntu/)
  * python 3.6
    * opencv-python
    * psutil
    * blosc
    * pika

Python packages can be pip installed via [requirements.txt](source/requirements.txt).


# Building
The docker file must be built before running. 
This only needs to be done once!
To do so run the following command:
```
sudo docker-compose -f source/generator/portable-gui.yml build
```
The build process will take several minutes.

---

# Running
To run the visual demo enter the following command:
```
cd source/
python visual.py
```

* You will be prompted for a password as the python script internally calls docker-compose. 
* It can take up to 30 seconds for the window to appear.
* It can take up to 30 seconds for the demo to shutdown properly!
* You may see many "run() Connection was closed, reconnecting...", this is normal.

### Options
* ``--domain <val>`` {cartpole, vizdoom}, defaults to vizdoom.
* ``--difficulty <val>`` {easy, medium, hard} defaults to easy.
* ``--novelty <val>`` defaults to 200.

Example:
```
python visual.py --domain cartpole --novelty 201 --difficulty easy
```

---

## Playing
To play select the OpenCV window and press the key corresponding to the desired action. 
One key press per action and frame update.

* Note: Two non-novel episodes will proceed the selected novel episodes.

### ViZDoom
* a &rarr; left 
* d &rarr;  right
* w &rarr; forward
* s&rarr; backward
* j&rarr; shoot
* k&rarr; turn left
* l&rarr; turn right
* q&rarr; QUIT
* any other key is nothing

### CartPole
* a &rarr; left
* d &rarr;  right
* w &rarr; forward
* s &rarr; backward
* q &rarr; QUIT
* any other key is nothing

# Notes
* The doom game engine is a frame late for updating ammo used. Shoot commands act immediately and the ammo graphic will be updated next tick.
* If you cannot use docker on your system due to privilege issues, the dockerfile contains the installation instructions. 
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
