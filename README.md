# DivRep: Repositories for Diversity-driven repair framework for E2E models.
---------------------
## Setup
### Carla Setup
```markdown
```bash
docker pull carlasim/carla:0.9.10
docker run --privileged --gpus all --net=host -e DISPLAY=$DISPLAY -e SDL_VIDEODRIVER=offscreen -v /usr/share/vulkan/icd.d:/usr/share/vulkan/icd.d -v /tmp/.X11-unix:/tmp/.X11-unix:rw carlasim/carla:0.9.10 /bin/bash ./CarlaUE4.sh -opengl -RenderOffScreen -carla-port=2000
```

### Python & Conda setup
- 
#### E2E model Setup
- [InterFuser: Interpretable End-to-End Urban Autonomous Driving](https://github.com/opendilab/InterFuser.git)
- [TCP: Trajectory-guided Control Prediction for End-to-end Autonomous Driving](https://github.com/OpenDriveLab/TCP)


## Diversity
- This repository is to demonstrate compute the diversity metrics GED-based distance for a failure frames. and it is revised from https://github.com/AICPS/roadscene2vec.git.
- File structure:
## Reproduction

