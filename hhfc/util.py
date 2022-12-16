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

import collections
import glob
import os

def find_driver_path(driver_name: str) -> str:
    """Find hwmon driver with name `driver_name` and returns the full path to
    its directory
    """
    drivers = list_system_drivers_paths()
    if driver_name in drivers:
        return drivers[name]
    else:
        raise FileNotFoundError(f"Driver with name {driver_name} not found.")

def list_system_drivers_paths() -> dict:
    """Look into hwmon sysfs all drivers names. It returns a dictionary with
    the driver name and full path of each one
    """
    base_path = "/sys/class/hwmon/"
    drivers = {}
    for hm_drv in os.listdir(base_path):
        full_path = base_path + hm_drv + "/"
        with open(full_path + "name", encoding="utf-8") as driver_path:
            name = driver_path.read().strip()
        drivers[name] = full_path

    return drivers

def list_fan_drivers() -> dict:
    """Looks into drivers list for fan controls. Any hwmon driver with any
    of this attributes is considered a fan (note that any driver can be both
    a fan and a sensor):
     - `fan*_input`
     - `fan*_target`
     - `pwm*`
    More than one fan can be detected for a single driver. Unusable drivers
    are filtered (like `pwm` attribute without correcponding `pwm_enable`).
    If none are detected, this returns an empty dict.
    """
    drivers = list_system_drivers_paths()
    fans = collections.defaultdict(dict)
    for name, path in drivers.items():
        fan_inputs = glob.glob('fan?_input', root_dir=path)
        fan_targets = glob.glob('fan?_target', root_dir=path)
        fan_enables = glob.glob('fan?_enable', root_dir=path)
        pwms = glob.glob('pwm?', root_dir=path)
        pwms_enable = glob.glob('pwm?_enable', root_dir=path)
        if fan_inputs:
            fans[name]["input"] = fan_inputs.sort()
        if pwms:
            # Remove unusable pwms
            for pwm in pwms:
                has_enable = False
                for enable in pwms_enable:
                    if pwm in enable:
                        has_enable = True
                if not has_enable:
                    del pwm
            fans[name]["pwm"] = pwms.sort()
        if fan_targets:
            # Remove unusable fant_targets
            for target in fan_targets:
                has_enable = False
                for enable in fan_enables:
                    if target[:4] in enable:
                        has_enable = True
                if not has_enable:
                    del target
            fans[name]["target"] = fan_targets.sort()

    return dict(fans)

def list_sensor_drivers() -> dict:
    """Looks into drivers list for temperature or power sensors. Any hwmon
    driver with any of this attributes is considered a sensor (note that any
    driver can be both a fan and a sensor):
     - `temp?_input`
     - `power?_average`
    More than one sensor can be detected for a single driver. If none are
    detected, this returns an empty dict.
    """
    drivers = list_system_drivers_paths()
    sensors = collections.defaultdict(dict)
    for name, path in drivers.items():
        temp_inputs = glob.glob('temp?_input', root_dir=path)
        power_averages = glob.glob('power?_average', root_dir=path)
        if temp_inputs:
            sensors[name]["temp"] = temp_inputs
        if power_averages:
            sensors[name]["power"] = power_averages

    return dict(sensors)
