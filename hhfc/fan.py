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

class Interpolator:
    """Interpolator of a curve between given points at initialization"""

    x_vals: list[int]
    y_vals: list[int]

    def __init__(self, x_vals: list[int], y_vals: list[int]):
        if not len(x_vals) == len(y_vals):
            raise ValueError("x_vals and y_vals need to be the same lenght")
        self.x_vals = x_vals
        self.y_vals = y_vals

    def _compute_l_poly_value(self, j: int, x: int) -> int:
        """Compute the j-th lagrange polynomial at point x"""
        k = len(self.x_vals)
        result = 1
        for m in range(k):
            if m == j:
                continue
            result *= (x - self.x_vals[m]) / (self.x_vals[j] - self.x_vals[m])
        return result

    def get_value(self, x: int) -> int:
        """Evaluate at x, if x is lower than the lowest x, return the lowest
        value
        """
        if x < self.x_vals[0]:
            return self.y_vals[0]
        if x > self.x_vals[-1]:
            return self.y_vals[-1]

        k = len(self.x_vals)
        result = 0
        for j in range(k):
            result += self.y_vals[j] * self._compute_l_poly_value(j, x)

        return result


class Fan:
    """Class to represent and control a fan"""

    name: str
    driver_name: str
    pwm_input: str
    pwm_enable: str
    fan_input: str
    min_val: int
    max_val: int
    allow_shutoff: bool
    min_allowed: int
    sensors: list[dict]
    interpolator: dict

    def __init__(self, fan_config: dict):
        full_path = util.find_driver_path(fan_config["driver_name"])

        self.name = fan_config["name"]
        self.driver_name = fan_config["driver_name"]
        self.fan_input = full_path + fan_config["fan_input"]
        self.pwm_enable = full_path + fan_config["handle"] + "_enable"
        self.pwm_input = full_path + fan_config["handle"]
        self.min_val = fan_config["min_control_value"]
        self.max_val = fan_config["max_control_value"]
        self.allow_shutoff = (fan_config["allow_shutoff"] == "yes")
        self.min_allowed = fan_config["minimum_duty_cycle"]
        self.sensors = fan_config["sensors"]
        self.interpolator = {
            sens["name"]:self._generate_interpolator(sens["name"]) for sens in self.sensors
        }

    def take_control(self) -> bool:
        """Atempt to take control of the fan from automatic control"""
        with open(self.pwm_enable, "r+", encoding="utf-8") as enable:
            enable.write("1")
        return self.check_control()

    def release_control(self) -> bool:
        """Atempt to take control of the fan from automatic control"""
        with open(self.pwm_enable, "r+", encoding="utf-8") as enable:
            enable.write("0")
        return not self.check_control()

    def check_control(self) -> bool:
        """Check if we are controlling this fan"""
        with open(self.pwm_enable, "r", encoding="utf-8") as enable:
            string = enable.read()
            return int(string) == 1

    def get_sensor_curve(self, sensor: str) -> dict:
        """Returns the curve for sensor."""
        for sens in self.sensors:
            if sens["name"] == sensor:
                return sens["curve"]
        raise ValueError(f"Not such sensor: {sensor}")

    def _generate_interpolator(self, sensor: str) -> Interpolator:
        """Returns a Interpolator object for given sensor name"""
        curve = self.get_sensor_curve(sensor)
        temps = [ column[0] for column in curve ]
        dutys = [ column[1] for column in curve ]
        return Interpolator(temps, dutys)

    def get_desired_duty_cycle(self, sensor: str, value: int) -> int:
        """Returns duty cycle for the current sensor state according to the
        specified curve
        """
        return self.interpolator[sensor].get_value(value)

    def set_duty_cycle(self, duty_cycle: int) -> None:
        """Sets duty cycle for this fan in the range [min_value-max_value]
        for the hwmon interface of choice. The input value `duty_cycle` should
        be in the range [0-100]. This function will scale acordingly.
        If the fan has shut-off policy set to "no" then it won't output a lower
        value than "minimum_duty_cycle".
        If the fan has shut-off policy set to "yes" then any value below
        "minimum_duty_cycle" will make the fan to turn off completely.
        """
        if duty_cycle < 0 or duty_cycle > 100:
            raise ValueError("Duty cycle has to be in the range [0-100]")

        # Enforce shutoff and min_value policy
        if duty_cycle <= self.min_allowed:
            if not self.allow_shutoff:
                duty_cycle = self.min_allowed
            else:
                duty_cycle = 0

        # Scale value
        duty = duty_cycle * (self.max_val - self.min_val) / 100.0

        if not self.check_control():
            raise IOError("Cant write to the fan control file")

        with open(self.pwm_input, "w", encoding="utf-8") as pwm:
            pwm.write(str(int(duty)))

    def read_input(self) -> int:
        """Read input for this fan. The value units are not converted"""
        with open(self.fan_input, "r", encoding="utf-8") as inp:
            return int(inp.read())

    def __str__(self) -> str:
        return (self.name + ": " + str(self.read_input()))

def fan_from_config(fan_config: dict) -> Fan:
    """Generate a Fan object with the configration passed as dictionary"""
    needed_keys = set(["name",
                       "driver_name",
                       "handle",
                       "max_control_value",
                       "min_control_value",
                       "fan_input"
                       ])

    if not needed_keys.issubset(fan_config.keys()):
        raise ValueError(f"Missing configuration. Needed {needed_keys}, "
                         "have {list(fan_config[name].keys())}")

    return Fan(fan_config)
