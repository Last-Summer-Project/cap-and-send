#!/usr/bin/env python3

from pi_sht1x import SHT1x
import RPi.GPIO as GPIO
import spidev


class Sensor:
    def __init__(self, sht_sck=18, sht_data=27, pin_spi_cs=8, adc_cds_ch=0, adc_soil_ch=1, spi_max_speed=1_000_000,
                 mode=GPIO.BCM):
        # sht 11
        self.pin_sht_sck = sht_sck
        self.pin_sht_data = sht_data
        self.mode = mode

        # adc (spi)
        # channel
        self.adc_cds_ch = adc_cds_ch
        self.adc_soil_ch = adc_soil_ch

        # setup
        self.pin_spi_cs = pin_spi_cs
        self.spi_max_speed = spi_max_speed

        # spi
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = self.spi_max_speed

    def read_sht(self):
        with SHT1x(self.pin_sht_data, self.pin_sht_sck, gpio_mode=self.mode) as sensor:
            temp = sensor.read_temperature()
            humidity = sensor.read_humidity(temp)
            sensor.calculate_dew_point(temp, humidity)
            return sensor.temperature_celsius, sensor.humidity, sensor.dew_point

    def read_adc(self, channel=0):
        GPIO.setmode(self.mode)
        GPIO.setup(self.pin_spi_cs, GPIO.OUT)

        # low cs Active
        GPIO.output(self.pin_spi_cs, 0)

        send_buff = [
            6 | (channel & 4) >> 2,
            ((channel & 3) << 6),
            0
        ]
        receive_buff = self.spi.xfer2(send_buff)

        n_adc_value = ((15 & receive_buff[1]) << 8) + receive_buff[2]

        # spi chip Select command
        GPIO.output(self.pin_spi_cs, 1)
        GPIO.cleanup()

        return n_adc_value

    def read_soil(self):
        return self.read_adc(self.adc_soil_ch)

    def read_cds(self):
        return self.read_adc(self.adc_cds_ch)

    def read_spi_all(self):
        return [self.read_adc(i) for i in range(7)]

    def read_all(self):
        return self.read_sht(), self.read_spi_all()

    def __del__(self):
        self.spi.close()
