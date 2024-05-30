# Home Assistant Crisp

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]

_Integration to integrate with [Crisp][crisp]._

## Crisp account

An instance of this integration provides information about a single Crisp account into Home Assistant.
The integration can be set up multiple times if you want to track multiple accounts.
An account is represented as a device.

## Account sensors

Name | Type | Description
-- | -- | --
`Order count total` | int | Total number of orders in your Crisp account (includes completed, cancelled and pending orders).
`Order count open` | int | Count of open orders in your Crisp account (out for delivery, or planned in the future).

## Next order sensors

If there are orders planned for delivery, the following sensors are available for the order that is closest to delivery.

Name | Type | Description
-- | -- | --
`Next order delivery on` | date | Delivery date
`Next order delivery start` | datetime | Start of the delivery window (as selected by the user)
`Next order delivery start time` | time | Start time of the delivery window (as selected by the user)
`Next order delivery end` | datetime | End of the delivery window (as selected by the user)
`Next order delivery end time` | time | End time of the delivery window (as selected by the user)
`Next order product count` | int | Number of order lines (count of different products, not a sum of counts)

## Installation using HACS

1. Open the HACS dashboard
2. Add this repository:
    1. Open the menu located in the top-right (the 3 dots)
    1. Select `Custom repositories`
    1. `Repository`: enter `https://github.com/NLthijs48/home-assistant-crisp`
    1. `Category`:  select `Integration`
    1. Click `Add`
    1. Close the popup
3. Search for `Crisp`, or click here:

[![Open your Home Assistant instance and open the Crisp repository inside the Home Assistant Community Store](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=NLthijs48&repository=home-assistant-crisp&category=integration)

4. Click the `Download` button in the bottom right corner
5. Confirm by clicking `Download`
6. Restart Home Assistant

## Set up the integration

1. In the HA UI go to `Configuration` > `Integrations` click `+` and search for `Crisp`, or click here:

[![Open your Home Assistant instance and start setting up the Crisp integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=crisp) 

2. Enter your email address that you use for your Crisp account
3. Enter the login code you receive on your email from Crisp
4. Done, entities should show up with information about your account

[![Open your Home Assistant instance and show the Crisp](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/integration/?domain=crisp)

## Manual installation

Copy all files from `custom_component/crisp/` to your HA installation, restart HA, configure the integration

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[crisp]: https://crisp.nl
[commits-shield]: https://img.shields.io/github/commit-activity/y/NLthijs48/home-assistant-crisp.svg?style=for-the-badge
[commits]: https://github.com/NLthijs48/home-assistant-crisp/commits/main
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/NLthijs48/home-assistant-crisp.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Thijs%20Wiefferink%20%40NLthijs48-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/NLthijs48/home-assistant-crisp.svg?style=for-the-badge
[releases]: https://github.com/NLthijs48/home-assistant-crisp/releases
