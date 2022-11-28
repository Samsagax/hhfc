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

from . import util


class Sensor:
    """Class to represent a hwmon Sensor"""

    name: str
    driver_name: str
    temp_input: str
    divisor: float
    offset: float
    curve: dict

    def __init__(self, sensor_config: dict):
        full_path = util.find_driver_path(sensor_config["driver_name"])

        self.name = sensor_config["name"]
        self.driver_name = sensor_config["driver_name"]
        self.sensor_input = full_path + sensor_config["temp_input"]
        self.divisor = sensor_config["divisor"] if "divisor" in sensor_config else 1
        self.offset = sensor_config["offset"] if "offset" in sensor_config else 0

    def read_input(self) -> float:
        """Check if we are controlling this fan"""
        with open(self.sensor_input, "r", encoding="utf-8") as raw_reading:
            return float(raw_reading.read()) / self.divisor + self.offset

    def __str__(self) -> str:
        """String representation of the sensor"""
        return str(self.name) + ": " + str(self.read_input())
