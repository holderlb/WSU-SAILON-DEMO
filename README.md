# Installation
* Requirments:
  * [docker](https://docs.docker.com/engine/install/ubuntu/)
  * python 3.6
    * 
    
# Building
The docker file must be built before running. To do so run the following command:
```
docker build -f Dockerfile-VISUAL -t wsudemo .
```
The build process will take several minutes.
    
# Running
To run the visual demo enter the following command:
```
python visual.py "user" "vizdoom" "base" "127.0.0.1" "55555"
```