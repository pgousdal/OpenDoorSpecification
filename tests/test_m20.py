import unittest
from ods_tools.adapters.daydream import DayDreamAdapter, RecordingDreamDoorBackend
from ods_tools.adapters.host import DoorDisconnected, DoorExit

class DayDreamAdapterTests(unittest.TestCase):
    def make(self):
        backend = RecordingDreamDoorBackend(
            account={"user_id": 42, "display_name": "Sysop"}, seconds_left=900,
            keys=["Y"], lines=["Open Door"])
        return DayDreamAdapter(backend, node=2), backend

    def test_verified_surface(self):
        adapter, backend = self.make()
        adapter.call("terminal.write", data="Hello")
        self.assertEqual(adapter.call("terminal.read_key"), "Y")
        self.assertEqual(adapter.call("terminal.read_line", max_length=4), "Open")
        self.assertEqual(adapter.call("session.identity")["user_id"], 42)
        self.assertEqual(adapter.call("session.node"), 2)
        self.assertEqual(adapter.call("session.time_left"), 900)
        adapter.call("status.set", text="Playing")
        adapter.call("bbs.command", command="WHO", arguments=[])
        self.assertEqual(backend.output, ["Hello"])
        self.assertEqual(backend.activity, "Playing")

    def test_carrier_loss_terminates_before_write(self):
        adapter, backend = self.make(); backend.connected = False
        with self.assertRaises(DoorDisconnected): adapter.write("never written")
        self.assertEqual(backend.output, [])

    def test_exit_closes_door(self):
        adapter, backend = self.make()
        with self.assertRaises(DoorExit): adapter.exit(7)
        self.assertEqual(backend.calls[-1]["symbol"], "CloseDoor")
        self.assertEqual(backend.calls[-1]["arguments"]["status"], 7)

    def test_all_core_operations_are_dispatchable(self):
        adapter, _ = self.make()
        expected = {
            "terminal.write", "terminal.read_key", "terminal.read_line",
            "session.identity", "session.node", "session.time_left",
            "session.connection_state", "status.set", "bbs.command",
            "lifecycle.exit", "lifecycle.disconnect",
        }
        self.assertEqual(adapter.operations, expected)

if __name__ == "__main__": unittest.main()
