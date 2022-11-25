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
    curve: dict

    def __init__(self, sensor_config: dict):
        full_path = util.find_driver_path(sensor_config["driver_name"])

        self.name = sensor_config["name"]
        self.driver_name = sensor_config["driver_name"]
        self.sensor_input = full_path + sensor_config["temp_input"]
        self.divisor = sensor_config["divisor"] if "divisor" in sensor_config else 1
        self.curve = sensor_config["curve"]

    def read_input(self) -> float:
        """Check if we are controlling this fan"""
        with open(self.sensor_input, "r", encoding="utf-8") as raw_reading:
            return float(raw_reading.read()) / self.divisor

    def get_desired_duty_cycle(self) -> int:
        """Returns duty cycle for the current sensor state according to the
        specified curve
        """
        value = self.read_input()
        if value <= self.curve["low"]["temp"]:
            return self.curve["low"]["duty"]
        if value >= self.curve["high"]["temp"]:
            return self.curve["high"]["duty"]

        # Get coefficients of the curve for quadratic interpolation
        xs = [
            self.curve["low"]["temp"],
            self.curve["mid"]["temp"],
            self.curve["high"]["temp"]
        ]
        ys = [
            self.curve["low"]["duty"],
            self.curve["mid"]["duty"],
            self.curve["high"]["duty"]
        ]

        duty = ys[0] * \
            (value - xs[1]) * (value - xs[2]) / \
                ((xs[0] - xs[1]) * (xs[0] - xs[2])) + \
            ys[1] * \
            (value - xs[2]) * (value - xs[0]) / \
                ((xs[1] - xs[2]) * (xs[1] - xs[0])) + \
            ys[2] * \
            (value - xs[0]) * (value - xs[1]) / \
                ((xs[2] - xs[0]) * (xs[2] - xs[1]))

        return duty

    def __str__(self) -> str:
        """String representation of the sensor"""
        return str(self.name) + ": " + str(self.read_input())
