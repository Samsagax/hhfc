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

import os

def find_driver_path(driver_name: str) -> str:
    """Find hwmon driver with name `driver_name` and returns the full path to
    its directory
    """
    base_path = "/sys/class/hwmon/"
    for driver in os.listdir(base_path):
        full_path = base_path + driver + "/"
        with open(full_path + "name", encoding="utf-8") as driver_path:
            test_name = driver_path.read().strip()
        if driver_name == test_name:
            return full_path

    raise RuntimeError(f"Driver with name {driver_name} not found.")
