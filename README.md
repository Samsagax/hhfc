# NOTE: This project is currently in the very early stages of development.

Is still on non-functional state but is published as a way to get feedback
and force me not to procrastinate it further.

# The Hwmon Handheld Fan Controller (hhfc)

This is meant to be a universal controller for anything that can be read
and writen from hwmon sysfs filesystem.
Originally designed for handhelds but can be configured for anything that has
sensors and fans exposed via hwmon sysfs (i.e. `/sys/class/hwmon/hwmon?/*`)

## Configuration

The driver uses FANS and SENSORS. Any FAN can watch one or more sensors.

Check the sample configuration file for details.

## Usage

Run `hhfc` with the standard configuration on `/etc/hhfc/fan_control.yaml`
by default.

To read from another location, use the `--config-file` option. `hhfc` would
need read permissions on the sensors files and write permissions on the fan
control files. For convenience a systemd unit is provided.

## Contributing

The project is under the GPLv3 license and all contributions are welcome.
