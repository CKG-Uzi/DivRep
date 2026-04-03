#!/usr/bin/env python

from __future__ import print_function

import operator
import py_trees
import random

import carla

import srunner.scenariomanager.scenarioatomics.atomic_trigger_conditions as conditions
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from srunner.scenariomanager.timer import TimeOut
from srunner.scenariomanager.weather_sim import WeatherBehavior
from srunner.scenariomanager.scenarioatomics.atomic_behaviors import UpdateAllActorControls


class BasicScenario(object):

    def __init__(self, name, ego_vehicles, config, world,
                 debug_mode=False, terminate_on_failure=False,
                 criteria_enable=False,
                 mutation_config=None, random_seed=None):

        self.other_actors = []
        if not self.timeout:
            self.timeout = 60

        self.criteria_list = []
        self.scenario = None

        self.ego_vehicles = ego_vehicles
        self.name = name
        self.config = config
        self.terminate_on_failure = terminate_on_failure

        self.mutation_config = mutation_config or {}
        self.random_seed = random_seed
        if self.random_seed is not None:
            random.seed(self.random_seed)
        self.mutation_log = {}

        self._initialize_environment(world)

        self._initialize_actors(config)
        if CarlaDataProvider.is_sync_mode():
            world.tick()
        else:
            world.wait_for_tick()

        if debug_mode:
            py_trees.logging.level = py_trees.logging.Level.DEBUG

        behavior = self._create_behavior()

        criteria = None
        if criteria_enable:
            criteria = self._create_test_criteria()

        behavior_seq = py_trees.composites.Sequence()
        trigger_behavior = self._setup_scenario_trigger(config)
        if trigger_behavior:
            behavior_seq.add_child(trigger_behavior)

        if behavior is not None:
            behavior_seq.add_child(behavior)
            behavior_seq.name = behavior.name

        end_behavior = self._setup_scenario_end(config)
        if end_behavior:
            behavior_seq.add_child(end_behavior)

        self.scenario = Scenario(behavior_seq, criteria, self.name, self.timeout, self.terminate_on_failure)

        if self.mutation_config:
            print(f"[Mutation] Scenario {self.name}: {self.mutation_log}")

    def _mutate(self, key, base_value, noise_range):
        if key in self.mutation_config:
            low, high = noise_range
            mutated = base_value + random.uniform(low, high)
            self.mutation_log[key] = mutated
            return mutated
        return base_value

    def _mutate_behavior_param(self, name, base, noise_range):
        return self._mutate(name, base, noise_range)

    def _initialize_environment(self, world):
        weather = self.config.weather

        if "weather_noise" in self.mutation_config:
            weather.cloudiness = self._mutate("cloudiness", weather.cloudiness, (-20, 20))
            weather.precipitation = self._mutate("rain", weather.precipitation, (-30, 30))

        world.set_weather(weather)

        if self.config.friction is not None:
            friction_bp = world.get_blueprint_library().find('static.trigger.friction')
            extent = carla.Location(1000000.0, 1000000.0, 1000000.0)
            friction_bp.set_attribute('friction', str(self.config.friction))
            friction_bp.set_attribute('extent_x', str(extent.x))
            friction_bp.set_attribute('extent_y', str(extent.y))
            friction_bp.set_attribute('extent_z', str(extent.z))

            transform = carla.Transform()
            transform.location = carla.Location(-10000.0, -10000.0, 0.0)
            world.spawn_actor(friction_bp, transform)

    def _initialize_actors(self, config):

        if config.other_actors:

            actors = list(config.other_actors)

            if "actor_removal_prob" in self.mutation_config:
                prob = self.mutation_config["actor_removal_prob"]
                actors = [a for a in actors if random.random() > prob]

            if "actor_keep_count" in self.mutation_config:
                k = self.mutation_config["actor_keep_count"]
                if k < len(actors):
                    actors = random.sample(actors, k)

            if "actor_position_noise" in self.mutation_config:
                for actor in actors:
                    t = actor.transform
                    dx = random.uniform(-self.mutation_config["actor_position_noise"],
                                        self.mutation_config["actor_position_noise"])
                    dy = random.uniform(-self.mutation_config["actor_position_noise"],
                                        self.mutation_config["actor_position_noise"])
                    t.location.x += dx
                    t.location.y += dy

            if "actor_yaw_noise" in self.mutation_config:
                for actor in actors:
                    t = actor.transform
                    dyaw = random.uniform(-10, 10)
                    t.rotation.yaw += dyaw

            new_actors = CarlaDataProvider.request_new_actors(actors)

            if not new_actors:
                raise Exception("Error: Unable to add actors")

            for new_actor in new_actors:
                self.other_actors.append(new_actor)

            self.mutation_log["num_actors_spawned"] = len(self.other_actors)

    def _setup_scenario_trigger(self, config):
        start_location = None
        if config.trigger_points and config.trigger_points[0]:
            start_location = config.trigger_points[0].location

            if "trigger_position_noise" in self.mutation_config:
                start_location.x += random.uniform(-5, 5)
                start_location.y += random.uniform(-5, 5)

        ego_vehicle_route = CarlaDataProvider.get_ego_vehicle_route()

        if start_location:
            trigger_distance = 5

            if "trigger_distance_noise" in self.mutation_config:
                trigger_distance = self._mutate("trigger_distance", trigger_distance, (-3, 10))

            if ego_vehicle_route:
                if config.route_var_name is None:
                    return conditions.InTriggerDistanceToLocationAlongRoute(
                        self.ego_vehicles[0],
                        ego_vehicle_route,
                        start_location,
                        trigger_distance
                    )
                else:
                    check_name = "WaitForBlackboardVariable: {}".format(config.route_var_name)
                    return conditions.WaitForBlackboardVariable(
                        name=check_name,
                        variable_name=config.route_var_name,
                        variable_value=True,
                        var_init_value=False
                    )

            return conditions.InTimeToArrivalToLocation(
                self.ego_vehicles[0],
                2.0,
                start_location
            )

        return None

    def _setup_scenario_end(self, config):
        ego_vehicle_route = CarlaDataProvider.get_ego_vehicle_route()

        if ego_vehicle_route:
            if config.route_var_name is not None:
                set_name = "Reset Blackboard Variable: {} ".format(config.route_var_name)
                return py_trees.blackboard.SetBlackboardVariable(
                    name=set_name,
                    variable_name=config.route_var_name,
                    variable_value=False
                )
        return None

    def _create_behavior(self):
        raise NotImplementedError

    def _create_test_criteria(self):
        raise NotImplementedError

    def change_control(self, control):
        return control

    def remove_all_actors(self):
        for i, _ in enumerate(self.other_actors):
            if self.other_actors[i] is not None:
                if CarlaDataProvider.actor_id_exists(self.other_actors[i].id):
                    CarlaDataProvider.remove_actor_by_id(self.other_actors[i].id)
                self.other_actors[i] = None
        self.other_actors = []


class Scenario(object):

    def __init__(self, behavior, criteria, name, timeout=60, terminate_on_failure=False):
        self.behavior = behavior
        self.test_criteria = criteria
        self.timeout = timeout
        self.name = name

        if self.test_criteria is not None and not isinstance(self.test_criteria, py_trees.composites.Parallel):
            for criterion in self.test_criteria:
                criterion.terminate_on_failure = terminate_on_failure

            self.criteria_tree = py_trees.composites.Parallel(
                name="Test Criteria",
                policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ONE
            )
            self.criteria_tree.add_children(self.test_criteria)
            self.criteria_tree.setup(timeout=1)
        else:
            self.criteria_tree = criteria

        self.timeout_node = TimeOut(self.timeout, name="TimeOut")

        self.scenario_tree = py_trees.composites.Parallel(
            name,
            policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ONE
        )

        if behavior is not None:
            self.scenario_tree.add_child(self.behavior)

        self.scenario_tree.add_child(self.timeout_node)
        self.scenario_tree.add_child(WeatherBehavior())
        self.scenario_tree.add_child(UpdateAllActorControls())

        if criteria is not None:
            self.scenario_tree.add_child(self.criteria_tree)

        self.scenario_tree.setup(timeout=1)

    def _extract_nodes_from_tree(self, tree):
        node_list = [tree]
        more_nodes_exist = True
        while more_nodes_exist:
            more_nodes_exist = False
            for node in node_list:
                if node.children:
                    node_list.remove(node)
                    more_nodes_exist = True
                    for child in node.children:
                        node_list.append(child)

        if len(node_list) == 1 and isinstance(node_list[0], py_trees.composites.Parallel):
            return []

        return node_list

    def get_criteria(self):
        return self._extract_nodes_from_tree(self.criteria_tree)

    def terminate(self):
        node_list = self._extract_nodes_from_tree(self.scenario_tree)

        for node in node_list:
            node.terminate(py_trees.common.Status.INVALID)

        actor_dict = {}
        try:
            check_actors = operator.attrgetter("ActorsWithController")
            actor_dict = check_actors(py_trees.blackboard.Blackboard())
        except AttributeError:
            pass

        for actor_id in actor_dict:
            actor_dict[actor_id].reset()

        py_trees.blackboard.Blackboard().set("ActorsWithController", {}, overwrite=True)