> :warning: NOTE: This project is currently in the very early stages of development.

# The Hwmon Handheld Fan Controller (hhfc)

This is meant to be a universal controller for anything that can be read
and writen from hwmon sysfs filesystem.
Originally designed for handhelds but can be configured for anything that has
sensors and fans exposed via hwmon sysfs exclusively
(i.e. `/sys/class/hwmon/hwmon?/*`)

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

## Usage

Run `hhfc` with a given configuration file. First clone the repo:
```shell
$ git clone https://github.com/Samsagax/hhfc/
$ cd hhfc
```
Then write your own configuration file for your machine and run the controller selecting the configuration file with the `-c` option:
```shell
# python -m hhfc -c fan_control.yaml
```

> :warning: You may need root privileges (i.e. sudo) to write to hwmon
> attribute files.

### Monitor mode
You can also run the controller in "monitor mode" by usign the `-m` flag.
This way the controller won't write to fan handles but can monitor sensor
readings and fan speeds.
```shell
# python -m hhfc -m -c fan_control.yaml
```

## Contributing

The project is under the GPLv3 license and all contributions are welcome.
