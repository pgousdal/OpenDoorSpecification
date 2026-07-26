import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/ods-tools/src"))

from ods_tools.adapters.host import DoorDisconnected, DoorExit, HostAdapter
from ods_tools.simulator import load_scenario, run_scenario


class HostAdapterTests(unittest.TestCase):
    def test_core_session_and_terminal_operations(self):
        adapter = HostAdapter(identity={"user_id": "7", "display_name": "Test"}, node=3, time_left=60)
        adapter.line_input.append("hello world")
        adapter.write("Prompt: ")
        self.assertEqual(adapter.read_line(max_length=5), "hello")
        self.assertEqual(adapter.get_identity()["user_id"], "7")
        self.assertEqual(adapter.get_node(), 3)
        self.assertEqual(adapter.get_time_left(), 60)
        self.assertEqual("".join(adapter.output), "Prompt: ")

    def test_disconnect_is_surfaced_before_terminal_io(self):
        adapter = HostAdapter(connected=False)
        with self.assertRaises(DoorDisconnected):
            adapter.write("not written")
        self.assertEqual(adapter.output, [])
        self.assertEqual(adapter.transcript[-1]["operation"], "lifecycle.disconnect")

    def test_exit_records_status(self):
        adapter = HostAdapter()
        with self.assertRaises(DoorExit) as caught:
            adapter.exit(20)
        self.assertEqual(caught.exception.status, 20)
        self.assertEqual(adapter.transcript[-1]["inputs"], {"status": 20})

    def test_bbs_commands_are_deny_by_default(self):
        adapter = HostAdapter()
        with self.assertRaises(KeyError):
            adapter.bbs_command("shell", ["echo", "unsafe"])
        adapter.register_command("who", lambda args: {"count": len(args)})
        self.assertEqual(adapter.bbs_command("who", [1, 2]), {"count": 2})

    def test_checked_in_scenario(self):
        scenario = load_scenario(ROOT / "examples/host-simulator/hello.json")
        result = run_scenario(scenario)
        self.assertEqual(result["termination"], {"kind": "exit", "status": 0})
        self.assertEqual(result["status"], "Running hello door")
        self.assertIn("Welcome to ODS!", result["output"])

    def test_adapter_catalog_covers_all_core_operations(self):
        operations = json.loads((ROOT / "catalog/operations/core.json").read_text())["operations"]
        adapter = json.loads((ROOT / "catalog/adapters/host-simulator.json").read_text())
        self.assertEqual({item["id"] for item in operations}, set(adapter["operations"]))


if __name__ == "__main__":
    unittest.main()
