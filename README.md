> :warning: NOTE: This project is currently in early stages of development and
> can change rapidly. Expect breakage between releases.

# The Hwmon Handheld Fan Controller (hhfc)

This is meant to be a universal controller for anything that can be read
and writen from hwmon sysfs filesystem.
Originally designed for handhelds but can be configured for anything that has
sensors and fans exposed via hwmon sysfs exclusively
(i.e. `/sys/class/hwmon/hwmon?/*`)

## Install
On ArchLinux (and derivatives) there is `hhfc-git` package in the
[AUR](https://aur.archlinux.org/packages/hhfc-git).

For installing from sources you'll need some python packages first:
 - `build`
 - `installer`
 - `wheel`
 - `setuptools`
 - `pyyaml`

Then clone sources and build/install

```shell
$ git clone git+https://github.com/Samsagax/hhfc.git
$ cd hhfc
$ python -m build --wheel
# python -m installer dist/*.whl
```

For system daemon use copy the systemd unit:
```shell
# cp -v systemd/hhfc.service /usr/lib/systemd/system/hhfc.service
```

## Usage
Run `hhfc` with a given configuration file:
```shell
$ hhfc -c fan_control.yaml
```

> :info: You may need root privileges (i.e. sudo) to write to hwmon
> attribute files.

There are some examples under `config` directory in the repo.
See [Configuration](#configuration) for writing your own for your machine

### Systemd unit (system daemon)
The most common usecase once configured is to run it as a system daemon.
Write a configuration file for your machine and place it in 
`/etc/hhfc/fan_control.yaml` (create directories if appropriate). Then enable
the systemd unit if not already. It will look for the system configuration and
start the daemon:
```shell
# systemctl enable hhfc.service
```

### Monitor mode
You can also run the controller in "monitor mode" by usign the `-m` flag.
This way the controller won't write to fan handles but can monitor sensor
readings and fan speeds.
```shell
# hhfc -m -c fan_control.yaml
```

## Configuration
The driver uses `FANS` and `SENSORS` as the configuration units defined on
a yaml file.

### Defining sensors
Sensors are read from hwmon drivers given it's name and temperature input.
Often the sensors need to be scaled and offset to have a readable value.

Example `SENSORS` section:
```yaml
SENSORS:
  - name: "cpu"
    driver_name: "k10temp"
    temp_input: "temp1_input"
    divisor: 1000
    offset: 20
  - name: "gpu"
    driver_name: "amdgpu"
    temp_input: "temp1_input"
    divisor: 1000
    offset: 20
```

- `name` defines how the sensor will be referenced by fans
- `driver_name` is the name of the hwmon driver to watch (i.e.
`/sys/class/hwmon?/name` attribute)
- `temp_input` name of the attribute file to read temperatures from.
- `divisor` the value to divide the read `temp_input`. Typical value is `1000`.
- `offset` the value to add to the read `temp_input` after the division. Most
chips expose the temperature with an offset of 20°C

Each sensor needs to be prepended with a list marker (i.e. `-`)

### Defining fans
Any fan can watch one or more sensors. It needs at least one to function. Fans
need to be defined by a name, the hwmon driver name and hwmon attribute to
handle and read its input.

Example `FANS` section:
```yaml
FANS:
  - name: "fan1"
    driver_name: "oxpec"
    handle: "pwm1"
    max_control_value: 255
    min_control_value: 0
    fan_input: "fan1_input"
    sensors:
      - name: "cpu"
        curve:
          low:
            temp: 50
            duty: 0
          mid:
            temp: 70
            duty: 50
          high:
            temp: 85
            duty: 100
      - name: "gpu"
        curve:
          low:
            temp: 50
            duty: 0
          mid:
            temp: 70
            duty: 50
          high:
            temp: 85
            duty: 100
```

- `name` is the name to reference this fan.
- `driver_name` is the name of the hwmon driver to write to (i.e.
`/sys/class/hwmon?/name` attribute)
- `handle` is the hwmon attribute file to write to (i.e.
`/sys/class/hwmon?/pwm1` in this case)
- `max_control_value` and `min_control_value` are the min and max value the
controller will write to the `handle`. Duty cycles are defined and used in the
[0-100] interval, written values will be mapped to [min-max] values before
writting.
- `fan_input` is the hwmon attribute to read fan speed from.
- `sensors` define a list of sensors and its curves this fan will monitor. Each
sensor curve definition needs to start with a list marker.
	- `name` is the sensor name that will be matched from the `SENSORS` section
	- `curve` defines three points with temperatires and corresponding duty
cycles. The `low` and `high` points will also work as cutoffs. Any temperature
value reading below the `low` defined `temp` will use the `duty` defined value
to write to the fan. Any value above `high` defined `temp` will use the `duty`
value to write to the fan (this is usually `100`)


## Contributing

The project is under the GPLv3 license and all contributions are welcome.
