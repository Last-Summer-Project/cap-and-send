# cap-and-send
Sensor data and Image collector for/on Raspberry Pi Kits

# Run
```bash
# install from apt
$ sudo apt install python3 python3-virtualenv python3-dev python3-pip python3-virtualenv python-is-python3
# config to enable GPIO, SPI in raspi-config
$ sudo raspi-config

# install and run
$ python -m virtualenv venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
$ python run.py
```
