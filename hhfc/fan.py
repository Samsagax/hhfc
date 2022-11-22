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


class Fan:
    """Class to represent and control a fan"""

    name: str
    driver_name: str
    pwm_input: str
    pwm_enable: str
    fan_input: str
    min_value: int
    max_value: int

    def __init__(self, fan_config: dict):
        full_path = util.find_driver_path(fan_config["driver_name"])

        self.name = fan_config["name"]
        self.driver_name = fan_config["driver_name"]
        self.fan_input = full_path + fan_config["fan_input"]
        self.pwm_enable = full_path + fan_config["handle"] + "_enable"
        self.pwm_input = full_path + fan_config["handle"]
        self.min_val = fan_config["min_control_value"]
        self.max_val = fan_config["max_control_value"]

    def take_control(self) -> bool:
        """Atempt to take control of the fan from automatic control"""
        with open(self.pwm_enable, "r+", encoding="utf-8") as enable:
            enable.write("1")
        return self.check_control()

    def check_control(self) -> bool:
        """Check if we are controlling this fan"""
        with open(self.pwm_enable, "r", encoding="utf-8") as enable:
            return enable.read() == "1"

    def set_duty_cycle(self, duty_cycle: int) -> None:
        """Sets duty cycle for this fan in the range [min_value-max_value]"""
        if duty_cycle < self.min_value or duty_cycle > self.max_value:
            raise ValueError("Duty cycle has to ve in the range "
                             f"[{self.min_value}-{self.max_value}]")

        if not self.check_control():
            raise IOError("Cant write to the fan control file")

        with open(self.pwm_input, "w", encoding="utf-8") as pwm:
            pwm.write(str(duty_cycle))


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
