"""
Copyright 2022 Joaquín I. Aramendía <samsagax at gmail dot com>

    This file is part of hhfc.

    hhfc is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

    hhfc is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
with hhfc. If not, see <https://www.gnu.org/licenses/>.
"""

import threading
from time import sleep
from hhfc.fan import Fan
from hhfc.sensor import Sensor


class Controller:
    """Class to represent a Controller. It handles Fans according to Sensors"""

    fans: list[Fan]
    sensors: list[Sensor]
    loop_interval: float
    monitor: bool
    exit_loop: threading.Event

    def __init__(self, fans: list[Fan], sensors: list[Sensor], loop_interval: float, monitor=False):
        self.fans = fans
        self.sensors = sensors
        self.loop_interval = loop_interval
        self.monitor = monitor
        self.exit_loop = threading.Event()

    def _loop_iter(self) -> None:
        sensor_readings = {}
        for sensor in self.sensors:
            sensor_readings[sensor.name] = sensor.read_input()

        print("Sensor readings: ")
        print(sensor_readings)

        for fan in self.fans:
            fan_duty = []
            for sensor in fan.sensors:
                if sensor["name"] in sensor_readings:
                    name = sensor["name"]
                    fan_duty.append(fan.get_desired_duty_cycle(name, sensor_readings[name]))
                else:
                    print(f"Sensor '{sensor['name']}' has no value for fan ('{fan.name}')")
            if not self.monitor:
                fan.set_duty_cycle(int(max(fan_duty)))
            print(f"fan {fan.name}: {fan.read_input()} RPM")

    def _loop(self) -> None:
        """Main control loop"""
        while True:
            self._loop_iter()
            if self.exit_loop.wait(timeout=self.loop_interval):
                return

    def get_sensors_for_fan(self, fan_idx: int) -> None:
        return self.fans[fan_idx]["sensors"]

    def run(self):
        """Runs the controller thread. This does not exit until interrupted"""

        # Set up
        print("Taking over fans")
        for fan in self.fans:
            try:
                print("Taking control of fan: " + fan.name)
                if not self.monitor:
                    fan.take_control()
            except Exception as exp:
                print("Could not take control of fan: " + fan.name)
                print(exp)

        self.exit_loop.clear()
        loop = threading.Thread(target=self._loop, daemon=False)

        print("Starting control loop")
        loop.start()

        try:
            loop.join()
        except (KeyboardInterrupt, SystemExit):
            print("Got Interrupt signal, exiting")
            self.exit_loop.set()
        except IOError as ioerr:
            print("Got IOError")
            self.exit_loop.set()
            print(ioerr)
        except Exception as exp:
            print("Uncaught Exception")
            self.exit_loop.set()
            print(exp)

        # Cleanup
        print("Restoring fans to automatic mode")
        for fan in self.fans:
            try:
                print("Release control of fan: " + fan.name)
                if not self.monitor:
                    fan.release_control()
            except Exception as exp:
                print("Could not restore fan: " + fan.name)
                print(exp)

