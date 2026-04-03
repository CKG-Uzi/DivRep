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
1. Download the carla leaderboard code for E2E models in:
- [InterFuser: Interpretable End-to-End Urban Autonomous Driving](https://github.com/opendilab/InterFuser.git)
- [TCP: Trajectory-guided Control Prediction for End-to-end Autonomous Driving](https://github.com/OpenDriveLab/TCP)
- Failure data collection: 
2. In `route_scenario.py`, update the collision criterion to terminate on failure.

**Before:**
```python
collision_criterion = CollisionTest(self.ego_vehicles[0], terminate_on_failure=False)
```
**After:**
```python
collision_criterion = CollisionTest(self.ego_vehicles[0], terminate_on_failure=True)
```
3. revise the following files to the carla leaderboard files for each model to collect the failure data in ```leaderboard```

## Reproducing the results
### RQ1. Effectiveness evaluation
The failure routes are all included in ```failure_routes```. Run the simulation of leaderboard following the codes,
in ```leaderboard/scripts/run_evaluation.sh```. This generate the mutated scenarios with the 

Then finetune the model in 
``` bash scripts/train.sh ``` with ```--epochs 5 --warmup-epochs 0 --lr 0.0005 --batch-size 4```

### RQ2. Parameter Evaluation
For generating the files with different configurations, revise the parameters in 
Then run ```bash RQ2_generation/repair_data_generation.sh --initial_failure_directory``` 







