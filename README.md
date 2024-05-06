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

## Sensors per account

Name | Description
-- | --
`Order count total` | Total number of orders in your Crisp account (includes completed, cancelled and pending orders).
`Order count open` | Count of open orders in your Crisp account (out for delivery, or planned in the future).

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `crisp`.
1. Download _all_ the files from the `custom_components/crisp/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Crisp"

### Configuration through the UI

1. Enter your email address that you use for your Crisp account
1. Enter the login code you receive on your email from Crisp
1. Done, entities should show up with information about your account

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
