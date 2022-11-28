import argparse
from hhfc import config, fan, sensor, controller


def arg_parse():
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

    return parser.parse_args()


def main():
    args = arg_parse()

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
