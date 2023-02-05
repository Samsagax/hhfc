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
import logging
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

        logging.debug("Sensor readings: %s", str(sensor_readings))

        for fan in self.fans:
            fan_duty = []
            for sensor in fan.sensors:
                if sensor["name"] in sensor_readings:
                    name = sensor["name"]
                    fan_duty.append(fan.get_desired_duty_cycle(name, sensor_readings[name]))
                else:
                    logging.warning("Sensor '%s' has no value for fan '%s'",
                                    sensor['name'],
                                    fan.name
                                    )
            if not self.monitor:
                fan.set_duty_cycle(int(max(fan_duty)))
                logging.debug("fan %s: %s RPM", fan.name, fan.read_input())
            else:
                logging.info("fan %s: %s RPM", fan.name, fan.read_input())

    def _loop(self) -> None:
        """Main control loop"""
        while True:
            self._loop_iter()
            if self.exit_loop.wait(timeout=self.loop_interval):
                return

    def _take_over_fans(self):
        """Put all fans in manual mode"""
        for fan in self.fans:
            try:
                logging.info("Taking control of fan: %s", fan.name)
                fan.take_control()
            except Exception as exp:
                logging.error("Could not take control of fan: %s", fan.name)
                logging.error(exp)

    def _release_fans(self):
        """Put all fans in automatic mode"""
        for fan in self.fans:
            try:
                logging.info("Release control of fan: %s", fan.name)
                fan.release_control()
            except Exception as exp:
                logging.error("Could not release fan: %s", fan.name)
                logging.error(exp)

    def get_sensors_for_fan(self, fan_idx: int) -> None:
        """Get the list of sensors for given fan index"""
        return self.fans[fan_idx]["sensors"]

    def run(self):
        """Runs the controller thread. This does not exit until interrupted"""

        # Set up
        if self.monitor:
            logging.info("Monitor mode, not taking over fans")
        else:
            logging.info("Taking over fans")
            self._take_over_fans()

        self.exit_loop.clear()
        loop = threading.Thread(target=self._loop, daemon=False)

        logging.debug("Starting control loop")
        loop.start()

        try:
            loop.join()
        except (KeyboardInterrupt, SystemExit):
            logging.info("Got Interrupt signal, bye!")
            self.exit_loop.set()
        except IOError as ioerr:
            logging.error("Got IOError: %s", ioerr)
            self.exit_loop.set()
        except Exception as exp:
            logging.warning("Uncaught Exception: %s", exp)
            self.exit_loop.set()

        # Cleanup
        if self.monitor:
            logging.info("Monitor mode, not restoring fans to automatic mode")
        else:
            logging.info("Restoring fans to automatic mode")
            self._release_fans()
