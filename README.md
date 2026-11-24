# Home Assistant Crisp

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]

_Integration to integrate with [Crisp][crisp]._

## Crisp account

An instance of this integration provides information about a single Crisp account into Home Assistant.
The integration can be set up multiple times if you want to track multiple accounts.
An account is represented as a device. The next order is represented as a separate "Next order" device linked to the account device.

## Account sensors

Name | Type | Description
-- | -- | --
`Order count total` | int | Total number of orders in your Crisp account (includes completed, cancelled and pending orders).
`Order count open` | int | Count of open orders in your Crisp account (out for delivery, or planned in the future).

## Next order sensors (device "Next order")

If there are orders planned for delivery, the following sensors are available for the order that is closest to delivery.

Name | Type | Description
-- | -- | --
`Delivery on` | date | Delivery date
`Delivery start` | datetime | Start of the delivery window (as selected by the user)
`Delivery expected` | datetime | Expected delivery time from track & trace (unavailable until a tracking link with an estimate is available)
`Delivery end` | datetime | End of the delivery window (as selected by the user)
`Product count` | int | Number of order lines (count of different products, not a sum of counts)
`Recipe count` | int | Number of recipes in the order (created by Crisp, possibly customized by the user)
`User recipe count` | int | Number of user-defined recipes in the order
`Mealkit count` | int | Number of mealkits in the order (0 if the order has no mealkit)
`Driver name` | string | First name of the driver (unavailable until the driver is known)
`Driver` | device tracker | Position of the delivery van (unavailable until the driver is on the way)

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

## Removing the integration

1. Go to **Settings** > **Devices & services** and select the Crisp integration
2. Click the three dots next to the Crisp account and choose **Delete**
3. If installed through the Marketplace, optionally remove the repository there; if installed manually, delete `custom_components/crisp/` and restart HA

## Quality scale

This integration targets the **Bronze** level of the Home Assistant integration quality scale. The status of each rule is tracked in [quality_scale.yaml](custom_components/crisp/quality_scale.yaml).

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Trademark Legal Notices

All product names, trademarks and registered trademarks in the images in this
repository, are property of their respective owners. All images in this
repository are used for identification purposes only.

## Integration blueprint

Thanks to ludeeus for the [integration blueprint](https://github.com/ludeeus/integration_blueprint) used as a starting point for this integration.

***

[crisp]: https://crisp.nl
[commits-shield]: https://img.shields.io/github/commit-activity/y/NLthijs48/home-assistant-crisp.svg?style=for-the-badge
[commits]: https://github.com/NLthijs48/home-assistant-crisp/commits/main
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/NLthijs48/home-assistant-crisp.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Thijs%20Wiefferink%20%40NLthijs48-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/NLthijs48/home-assistant-crisp.svg?style=for-the-badge
[releases]: https://github.com/NLthijs48/home-assistant-crisp/releases
