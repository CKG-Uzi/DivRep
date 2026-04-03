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
```markdown
```bash
- pip install -r requirements.txt
```
#### E2E model Setup
- [InterFuser: Interpretable End-to-End Urban Autonomous Driving](https://github.com/opendilab/InterFuser.git)
- [TCP: Trajectory-guided Control Prediction for End-to-end Autonomous Driving](https://github.com/OpenDriveLab/TCP)
- Failure data collection: 
1. In `route_scenario.py`, update the collision criterion to terminate on failure.

**Before:**
```python
collision_criterion = CollisionTest(self.ego_vehicles[0], terminate_on_failure=False)
collision_criterion = CollisionTest(self.ego_vehicles[0], terminate_on_failure=True)
```
2. revise the following files to the carla leaderboard files for each model to collect the failure data, as shown in ```leaderboard```

- Mutation of existing scenarios:




## Reproducing the results
### RQ1. Effectiveness evaluation






