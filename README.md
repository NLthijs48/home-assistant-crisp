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
`Next order delivery end` | datetime | End of the delivery window (as selected by the user)
`Next order product count` | int | Number of order lines (count of different products, not a sum of counts)

## Installation from the Marketplace

[![Open your Home Assistant instance and open a repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=NLthijs48&repository=home-assistant-crisp&category=integration)

## Installation as a custom repository
1. Go the the Marketplace in Home Assistant [![Open your Home Assistant instance and show the custom repositories you added to the Marketplace.](https://my.home-assistant.io/badges/marketplace_repositories.svg)](https://my.home-assistant.io/redirect/marketplace_repositories/)
2. Click `Add from link`
3. Paste the link to this repository in there: `https://github.com/NLthijs48/home-assistant-crisp`
4. Click `Add`

## Set up the integration

1. Select the country of your Crisp account
2. Enter your email address that you use for your Crisp account
3. Enter the login code you receive on your email from Crisp
4. Done, entities should show up with information about your account

[![Open your Home Assistant instance and show the Crisp](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/integration/?domain=crisp)

## Manual installation

Copy all files from `custom_component/crisp/` to your HA installation, restart HA, configure the integration

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Trademark Legal Notices

All product names, trademarks and registered trademarks in the images in this
repository, are property of their respective owners. All images in this
repository are used for identification purposes only.

***

[crisp]: https://crisp.nl
[commits-shield]: https://img.shields.io/github/commit-activity/y/NLthijs48/home-assistant-crisp.svg?style=for-the-badge
[commits]: https://github.com/NLthijs48/home-assistant-crisp/commits/main
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/NLthijs48/home-assistant-crisp.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Thijs%20Wiefferink%20%40NLthijs48-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/NLthijs48/home-assistant-crisp.svg?style=for-the-badge
[releases]: https://github.com/NLthijs48/home-assistant-crisp/releases
