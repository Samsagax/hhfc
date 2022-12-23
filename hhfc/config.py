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

import yaml

# Default valoes for configuration
## Controller
DEFAULT_INTERVAL = 1.0

## Sensors
DEFAULT_SENSOR_DIVISOR = 1000
DEFAULT_SENSOR_OFFSET = 0

## Fans
DEFAULT_FAN_MIN_CONTROL_VALUE = 0
DEFAULT_FAN_MAX_CONTROL_VALUE = 255
DEFAULT_FAN_ALLOW_SHUTOFF = "no"
DEFAULT_FAN_MINIMUM_DUTY_CYCLE = 30


class Config:
    """Class to manage configuration files"""

    config: dict

    def __init__(self, file_path: str, auto_load: bool = False):
        self.file_path = file_path
        self.config = None
        if auto_load:
            self._read_configuration()

    def _read_configuration(self) -> None:
        """Users should not call this function directly, would be called when
        config is needed
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file)

        # Set default values if not configured
        if "INTERVAL" not in self.config:
            self.config["INTERVAL"] = DEFAULT_INTERVAL

        for sensor in self.get_sensors_config():
            if "divisor" not in sensor:
                sensor["divisor"] = DEFAULT_SENSOR_DIVISOR
            if "offset" not in sensor:
                sensor["offset"] = DEFAULT_SENSOR_OFFSET

        for fan in self.get_fans_config():
            if "max_control_value" not in fan:
                fan["max_control_value"] = DEFAULT_FAN_MAX_CONTROL_VALUE
            if "min_control_value" not in fan:
                fan["mim_control_value"] = DEFAULT_FAN_MIN_CONTROL_VALUE
            if "allow_shutoff" not in fan:
                fan["allow_shutoff"] = DEFAULT_FAN_ALLOW_SHUTOFF
            if "minimum_duty_cycle" not in fan:
                fan["minimum_duty_cycle"] = DEFAULT_FAN_MINIMUM_DUTY_CYCLE

    def get_full_config(self) -> dict:
        """Get entire read dictionary, used for debug, mostly"""
        if not self.config:
            self._read_configuration()

        return self.config

    def get_fans_config(self, fan_idx: int = None) -> dict:
        """Returns a dictionary with fan configuration data"""
        if not self.config:
            self._read_configuration()

        return self.config["FANS"][fan_idx] \
            if (fan_idx is not None) else \
            self.config["FANS"]

    def get_sensors_config(self, sensor_idx: int = None) -> dict:
        """Returns a dictionary with sensors configuration data"""
        if not self.config:
            self._read_configuration()

        return self.config["SENSORS"][sensor_idx] \
            if (sensor_idx is not None) else \
            self.config["SENSORS"]

    def get_interval(self) -> float:
        """Returns interval data from configuration"""
        if not self.config:
            self._read_configuration()

        return self.config["INTERVAL"]
