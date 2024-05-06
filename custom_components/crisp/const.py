"""Constants for crisp."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "Crisp"
DOMAIN = "crisp"
VERSION = "1.0.0"
ATTRIBUTION = "Data provided by Crisp"

# Sensor entity id keys
SENSOR_ORDER_COUNT_TOTAL = "order_count_total"
SENSOR_ORDER_COUNT_OPEN = "order_count_open"

# Coordinator data keys
ORDER_COUNT_TOTAL_KEY = "order_count_total"
ORDER_COUNT_OPEN_KEY = "order_count_open"
