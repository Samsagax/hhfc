# The Hwmon Handheld Fan Controller (hhfc)

This is meant to be a universal controller for anything that can be read from
hwmon sysfs filesystem. Originally designed for handhelds but can be configured
for anything that has sensors and fans.

## Configuration

Check the sample configuration file

## Usage

Run `hhfc` with the standard configuration on `/etc/hhfc/fan_control.yaml`
by default.

To read from another location, use the `--config-file` option. `hhfc` would
need read permissions on the sensors files and write permissions on the fan
control files. For convenience a systemd unit is provided.

## Contributing

The project is under the GPLv3 license and all contributions are welcome.
