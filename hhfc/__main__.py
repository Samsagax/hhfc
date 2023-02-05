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

import argparse
import logging
from hhfc import config, fan, sensor, controller


def arg_parse():
    """Basic argument parsing"""
    parser = argparse.ArgumentParser(
        description="Hwmon Handheld Fan Controller (hhfc)"
    )
    parser.add_argument('-c', '--config-file',
                        action='store',
                        type=str,
                        default="fan_control.yaml",
                        help="Configuration file path"
                        )
    parser.add_argument('-m', '--monitor',
                        action='store_true',
                        help="Monitor mode. When set the fans duty cycles are not modified"
                        )
    parser.add_argument('-l', '--loglevel',
                        action='store',
                        type=str,
                        default="INFO",
                        help="Log level to output (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
                        )

    return parser.parse_args()


def setup_logging(loglevel):
    """Setup logging level from command line parameters"""
    match loglevel:
        case 'DEBUG':
            level = logging.DEBUG
        case 'INFO':
            level = logging.INFO
        case 'WARNING':
            level = logging.WARNING
        case 'ERROR':
            level = logging.ERROR
        case 'CRITICAL':
            level = logging.CRITICAL
        case _:
            level = logging.INFO
    logging.basicConfig(level=level)


def main():
    """The main application logic"""
    args = arg_parse()

    # Setup logging
    setup_logging(args.loglevel)

    # Read configuration
    conf = config.Config(args.config_file)

    fan_list = []
    for fan_conf in conf.get_fans_config():
        fan_list.append(fan.Fan(fan_conf))

    sensor_list = []
    for sensor_conf in conf.get_sensors_config():
        sensor_list.append(sensor.Sensor(sensor_conf))

    interval = conf.get_interval()

    control = controller.Controller(fan_list, sensor_list, interval, args.monitor)
    control.run()


if __name__ == '__main__':
    main()
