"""Offline regression tests for planner-to-agent dependency expansion.

Run from the repository root with:
    python -m unittest discover -s tests -p 'test_task_manager_dependencies.py' -v

The actual TaskManager, Task, Graph, and controller modules are loaded. Only
optional model/environment/retrieval/plotting imports and external side effects
are stubbed; no LLM, Minecraft server, network, or third-party packages are needed.
"""

import copy
import importlib.util
import itertools
import json
import logging
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]


def stub_module(name, **attributes):
    module = types.ModuleType(name)
    module.__dict__.update(attributes)
    return module


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_offline_modules():
    stubs = {
        "networkx": stub_module("networkx", DiGraph=Mock),
        "matplotlib": stub_module("matplotlib"),
        "matplotlib.pyplot": stub_module("matplotlib.pyplot"),
        "pipeline.data_manager": stub_module("pipeline.data_manager", DataManager=Mock),
        "pipeline.retriever": stub_module("pipeline.retriever", Retriever=Mock),
        "model.openai_models": stub_module("model.openai_models", OpenAILanguageModel=type("UnusedModel", (), {})),
        "model.init_model": stub_module("model.init_model", init_language_model=Mock),
        "pipeline.agent": stub_module("pipeline.agent", BaseAgent=Mock),
        "pipeline.controller_prompt": stub_module("pipeline.controller_prompt"),
        "env.env": stub_module("env.env", VillagerBench=Mock),
        "pipeline.utils": stub_module(
            "pipeline.utils",
            init_logger=lambda *args, **kwargs: logging.getLogger("dependency-test"),
            format_string=lambda template, data: template,
            extract_info=lambda response, **kwargs: json.loads(response),
        ),
    }
    # Module imports append cwd to sys.path; restore it and sys.modules afterwards
    # so this isolated harness does not replace real application imports elsewhere.
    with patch.dict(sys.modules, stubs), patch.object(sys, "path", list(sys.path)):
        graph = load_module("type_define.graph", "type_define/graph.py")
        load_module("pipeline.task_prompt", "pipeline/task_prompt.py")
        manager = load_module("pipeline.task_manager", "pipeline/task_manager.py")
        controllers = [
            load_module("pipeline.controller", "pipeline/controller.py"),
            load_module("pipeline.controller_tiny", "pipeline/controller_tiny.py"),
        ]
    return graph, manager, controllers


graph_module, manager_module, controller_modules = load_offline_modules()
Task = graph_module.Task
Graph = graph_module.Graph
TaskManager = manager_module.TaskManager


def row(task_id, description, agents, dependencies):
    return {
        "id": task_id,
        "description": description,
        "assigned agents": agents,
        "required subtasks": dependencies,
        "milestones": [description],
        "retrieval paths": [],
    }


def edge_ids(graph):
    return {(graph.vertex.index(a) + 1, graph.vertex.index(b) + 1) for a, b in graph.edge}


class TaskManagerDependencyTests(unittest.TestCase):
    def setUp(self):
        self.agents = [types.SimpleNamespace(name="Alice"), types.SimpleNamespace(name="Bob")]
        # The constructor performs unrelated filesystem cleanup. Avoid it, and
        # provide only the collaborators used by the real init/update methods.
        self.manager = TaskManager.__new__(TaskManager)
        self.manager.logger = Mock()
        self.manager.agent_list = self.agents
        self.manager.manage_method = "update"
        self.manager.cache_enabled = False
        self.manager.dm = Mock()
        self.manager.dm.query_env_with_task.return_value = "test environment"
        self.manager.dm.query_history.return_value = "test history"
        self.manager.task_description = "Make a cake"
        self.manager.task_document = {}
        self.manager.task_trace_description = []
        self.manager.total_trace_description = []
        self.manager.fail_trace_description = []
        self.manager.update_history = Mock()
        self.manager.llm = Mock()
        self.addCleanup(patch.stopall)
        patch.object(Graph, "write_graph_to_md").start()
        patch.object(Graph, "write_graph_to_json").start()

    def build(self, plan, method="init_task"):
        self.manager.llm.few_shot_generate_thoughts.return_value = json.dumps(plan)
        if method == "init_task":
            self.manager.init_task("Make a cake")
        else:
            self.manager.update_task(Task("previous task", {}))
        self.assertEqual(self.manager.status, TaskManager.idle)
        return self.manager.graph

    def issue_plan(self):
        return [
            row(1, "Collect ingredients", ["Alice", "Bob"], []),
            row(2, "Craft cake", ["Alice", "Bob"], [1]),
        ]

    def test_issue_10_expands_dependencies_to_every_agent(self):
        expanded = self.manager.fill_agents(self.issue_plan(), self.agents)
        self.assertEqual([r["id"] for r in expanded], [1, 2, 3, 4])
        self.assertEqual([r["assigned agents"] for r in expanded], [["Alice"], ["Bob"], ["Alice"], ["Bob"]])
        self.assertEqual([r["required subtasks"] for r in expanded], [[], [], [1, 2], [1, 2]])

    def test_issue_10_init_and_update_build_complete_group_edges(self):
        for method in ("init_task", "update_task"):
            with self.subTest(method=method):
                graph = self.build(self.issue_plan(), method)
                self.assertEqual(edge_ids(graph), {(1, 3), (2, 3), (1, 4), (2, 4)})
                self.assertTrue(all(t.number == 1 for t in graph.vertex))
                self.assertEqual([t.candidate_list for t in graph.vertex], [["Alice"], ["Bob"], ["Alice"], ["Bob"]])

    def test_update_keeps_immediate_single_agent_prerequisite(self):
        plan = [row(1, "Collect", ["Alice"], []), row(2, "Craft", ["Bob"], [1])]
        for method in ("init_task", "update_task"):
            with self.subTest(method=method):
                self.assertEqual(edge_ids(self.build(plan, method)), {(1, 2)})

    def test_mixed_groups_remap_shifted_original_ids(self):
        plan = [row(1, "Collect", ["Alice", "Bob"], []),
                row(2, "Prepare", ["Alice"], [1]),
                row(3, "Craft", ["Bob"], [2])]
        for method in ("init_task", "update_task"):
            with self.subTest(method=method):
                self.assertEqual(edge_ids(self.build(plan, method)), {(1, 3), (2, 3), (3, 4)})

    def test_multiple_prerequisite_groups_are_all_preserved(self):
        plan = [row(1, "Collect", ["Alice", "Bob"], []),
                row(2, "Prepare", ["Alice"], []),
                row(3, "Craft", ["Bob"], [1, 2])]
        for method in ("init_task", "update_task"):
            with self.subTest(method=method):
                self.assertEqual(edge_ids(self.build(plan, method)), {(1, 4), (2, 4), (3, 4)})

    def test_explicit_single_agent_plan_remains_unchanged(self):
        plan = [row(1, "Alice collects", ["Alice"], []),
                row(2, "Bob collects", ["Bob"], []),
                row(3, "Alice crafts", ["Alice"], [1, 2]),
                row(4, "Bob crafts", ["Bob"], [1, 2])]
        for method in ("init_task", "update_task"):
            with self.subTest(method=method):
                self.assertEqual(edge_ids(self.build(plan, method)), {(1, 3), (2, 3), (1, 4), (2, 4)})

    def test_empty_dependencies_keep_existing_parallel_sibling_inheritance(self):
        plan = [row(1, "Collect", ["Alice", "Bob"], []),
                row(2, "Prepare", ["Alice"], [1]),
                row(3, "Craft", ["Bob"], [])]
        for method in ("init_task", "update_task"):
            with self.subTest(method=method):
                self.assertEqual(edge_ids(self.build(plan, method)), {(1, 3), (2, 3), (1, 4), (2, 4)})

    def test_omitted_dependencies_match_empty_dependencies(self):
        plan = self.issue_plan()
        del plan[0]["required subtasks"]
        for method in ("init_task", "update_task"):
            with self.subTest(method=method):
                self.assertEqual(edge_ids(self.build(plan, method)), {(1, 3), (2, 3), (1, 4), (2, 4)})

    def test_independent_groups_do_not_gain_serial_edges(self):
        plan = self.issue_plan()
        plan[1]["required subtasks"] = []
        for method in ("init_task", "update_task"):
            with self.subTest(method=method):
                self.assertEqual(edge_ids(self.build(plan, method)), set())

    def test_missing_ids_fall_back_to_original_one_based_positions(self):
        plan = self.issue_plan()
        for task in plan:
            del task["id"]
        self.assertEqual(edge_ids(self.build(plan)), {(1, 3), (2, 3), (1, 4), (2, 4)})

    def test_declared_ids_are_used_instead_of_expanded_positions(self):
        plan = [row("10", "Collect", ["Alice", "Bob"], []),
                row("20", "Craft", ["Bob"], ["10"])]
        self.assertEqual(edge_ids(self.build(plan)), {(1, 3), (2, 3)})

    def test_chronology_follows_list_order_not_numeric_id_order(self):
        plan = [row(30, "Collect", ["Alice", "Bob"], []),
                row(10, "Prepare", ["Alice"], [30]),
                row(20, "Craft", ["Bob"], [10])]
        self.assertEqual(edge_ids(self.build(plan)), {(1, 3), (2, 3), (3, 4)})

    def test_legacy_query_graph_callsite_keeps_positional_and_default_semantics(self):
        tasks = [Task("Collect", {}), Task("Prepare", {}), Task("Craft", {})]
        tasks[1]._pre_idxs = [1]
        self.assertEqual(edge_ids(self.manager.query_graph(tasks)), {(1, 2), (1, 3)})
        # query_graph is also called directly by merge_task; its existing
        # explicit zero sentinel does not inherit the previous predecessors.
        tasks[2]._pre_idxs = [0]
        self.assertEqual(edge_ids(self.manager.query_graph(tasks)), {(1, 2)})

    def test_repeated_prerequisites_do_not_duplicate_expanded_ids(self):
        plan = self.issue_plan()
        plan[1]["required subtasks"] = [1, "1"]
        expanded = self.manager.fill_agents(plan, self.agents)
        self.assertEqual(expanded[2]["required subtasks"], [1, 2])

    def test_input_and_sibling_dependency_lists_are_not_mutated(self):
        plan = self.issue_plan()
        original = copy.deepcopy(plan)
        expanded = self.manager.fill_agents(plan, self.agents)
        self.assertEqual(plan, original)
        expanded[2]["required subtasks"].append(99)
        self.assertEqual(expanded[3]["required subtasks"], [1, 2])
        self.assertEqual(plan, original)

    def test_invalid_agent_replacement_is_preserved(self):
        plan = [row(1, "Collect", ["Unknown"], [])]
        with patch.object(manager_module.random, "choice", return_value=self.agents[1]):
            expanded = self.manager.fill_agents(plan, self.agents)
        self.assertEqual(expanded[0]["assigned agents"], ["Bob"])
        self.assertEqual(plan[0]["assigned agents"], ["Unknown"])

    def test_empty_plan_is_supported(self):
        for method in ("init_task", "update_task"):
            with self.subTest(method=method):
                graph = self.build([], method)
                self.assertEqual(graph.vertex, [])
                self.assertEqual(graph.edge, [])

    def test_ambiguous_or_invalid_planner_ids_are_rejected(self):
        for ids in ([1, 1], [1, "1"], [0, 2], [-1, 2], [True, 2],
                    [1.5, 2], [None, 2], ["invalid", 2]):
            with self.subTest(ids=ids):
                plan = self.issue_plan()
                for task, task_id in zip(plan, ids):
                    task["id"] = task_id
                with self.assertRaisesRegex(ValueError, "[Ii][Dd]s"):
                    self.manager.fill_agents(plan, self.agents)

    def test_explicit_id_cannot_collide_with_missing_id_fallback(self):
        plan = self.issue_plan()
        plan[0]["id"] = 2
        del plan[1]["id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            self.manager.fill_agents(plan, self.agents)

    def test_invalid_explicit_dependencies_are_not_replaced_with_inheritance(self):
        for dependencies in ([99], [0], [-1], [True], [1.5], ["invalid"], [None]):
            with self.subTest(dependencies=dependencies):
                plan = [row(1, "Collect", ["Alice"], []),
                        row(2, "Prepare", ["Bob"], [1]),
                        row(3, "Craft", ["Alice"], dependencies)]
                with self.assertRaises(ValueError):
                    self.manager.fill_agents(plan, self.agents)

    def test_self_and_forward_references_are_rejected_before_graph_recursion(self):
        for dependencies in ([1], [2]):
            with self.subTest(dependencies=dependencies):
                plan = self.issue_plan()
                plan[0]["required subtasks"] = dependencies
                with self.assertRaisesRegex(ValueError, "earlier tasks"):
                    self.manager.fill_agents(plan, self.agents)

    def test_dependency_on_unassigned_task_is_rejected(self):
        plan = self.issue_plan()
        plan[0]["assigned agents"] = []
        with self.assertRaisesRegex(ValueError, "no assigned agents"):
            self.manager.fill_agents(plan, self.agents)

    def test_rejected_plan_leaves_manager_idle_and_previous_graph_intact(self):
        for method in ("init_task", "update_task"):
            with self.subTest(method=method):
                previous_graph = self.build(self.issue_plan())
                plan = self.issue_plan()
                plan[1]["required subtasks"] = [99]
                with self.assertRaisesRegex(ValueError, "unknown task"):
                    self.build(plan, method)
                self.assertEqual(self.manager.status, TaskManager.idle)
                self.assertIs(self.manager.graph, previous_graph)

    def test_unreferenced_unassigned_task_is_still_omitted(self):
        plan = [row(1, "Unused", [], []), row(2, "Collect", ["Alice"], [])]
        graph = self.build(plan)
        self.assertEqual([t.description for t in graph.vertex], ["Collect"])
        self.assertEqual(graph.edge, [])

    def test_generated_chronological_plans_preserve_source_graph_dependencies(self):
        # Exhaust all 64 three-task combinations of one/two agents and valid
        # prerequisite subsets, then exercise both graph-construction paths.
        for widths in itertools.product((1, 2), repeat=3):
            for second, third in itertools.product(([], [1]), ([], [1], [2], [1, 2])):
                plan = [row(i, "Task " + str(i), [a.name for a in self.agents[:width]], deps)
                        for i, width, deps in zip((1, 2, 3), widths, ([], second, third))]
                groups = []
                next_id = 1
                for width in widths:
                    groups.append(list(range(next_id, next_id + width)))
                    next_id += width
                expected = set()
                previous_dependencies = []
                for group, task in zip(groups, plan):
                    dependencies = task["required subtasks"] or previous_dependencies
                    for predecessor in dependencies:
                        expected.update(itertools.product(groups[predecessor - 1], group))
                    previous_dependencies = dependencies
                for method in ("init_task", "update_task"):
                    with self.subTest(widths=widths, second=second, third=third, method=method):
                        self.assertEqual(edge_ids(self.build(plan, method)), expected)

    def test_both_controllers_wait_for_every_expanded_prerequisite(self):
        for method in ("init_task", "update_task"):
            for controller_module in controller_modules:
                with self.subTest(method=method, controller=controller_module.__name__):
                    graph = self.build(self.issue_plan(), method)
                    controller = controller_module.GlobalController.__new__(controller_module.GlobalController)
                    controller.agent_list = self.agents
                    controller.name_list = [a.name for a in self.agents]
                    controller.assignment = {}
                    graph.vertex[0].status = Task.success
                    graph.vertex[1].status = Task.running
                    controller.task_list = graph.get_open_task_list()
                    self.assertEqual(controller.check_task_list_available(), [])
                    graph.vertex[1].status = Task.success
                    controller.task_list = graph.get_open_task_list()
                    self.assertEqual(controller.check_task_list_available(), graph.vertex[2:])


if __name__ == "__main__":
    unittest.main()
