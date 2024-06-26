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
SENSOR_NEXT_ORDER_PRODUCT_COUNT = "next_order_product_count"
SENSOR_NEXT_ORDER_DELIVERY_ON = "next_order_delivery_on"
SENSOR_NEXT_ORDER_DELIVERY_START = "next_order_delivery_start"
SENSOR_NEXT_ORDER_DELIVERY_START_TIME = "next_order_delivery_start_time"
SENSOR_NEXT_ORDER_DELIVERY_END = "next_order_delivery_end"
SENSOR_NEXT_ORDER_DELIVERY_END_TIME = "next_order_delivery_end_time"
