# Slot Bot

## Description

Slot Bot is a high-performance Discord bot designed to streamline slot management in your server. It allows users to create slots for various purposes, such as selling items or offering services. The bot includes features like creating, renewing, holding, and unholding slots, as well as adding and removing users from slots.

## Features

- Create slots with specified durations and categories
- Renew slots with updated durations
- Hold slots temporarily
- Unhold slots when ready
- Add and remove users from slots
- Set slot rules and guidelines
- Receive notifications for slot activities

## Usage

To use the bot, follow these steps:

1. **Create a Slot:** Use the `,create` command to create a new slot. Example: `,create @user 1 d category1 4 Slot`.

2. **Add Users:** Use the `,add` command to add users to a slot. Example: `,add @user`.

3. **Renew a Slot:** Use the `,renew` command to renew a slot with updated duration. Example: `,renew @user #channel 1 m/d his Slot`.

4. **Hold a Slot:** Use the `,hold` command to temporarily hold a slot.

5. **Unhold a Slot:** Use the `,unhold` command to unhold a slot.

6. **Remove Users:** Use the `,remove` command to remove users from a slot. Example: `,remove @user`.

7. **Ping Notification:** Use the `,ping` command to receive a notification in the slot channel. Example: `,ping`.

## Installation

To install the bot, follow these steps:

1. Clone the repository: `git clone https://github.com/codewithriza/SlotBot.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your configuration: Create a `config.json` file with your bot token, category ID, staff ID, etc. Make sure to keep your bot token private and secure.
4. Replace token and other guild id, channel id, 2 category id in `main.py`
5. Run the bot: `python main.py`

> [!IMPORTANT]
> Ensure that your bot token is kept private and setup in config.json along with category id staff id etc create separate category for 1 and 2 and read through the code to understand

## Contributing

Contributions are welcome! If you have any ideas or improvements, feel free to open an issue or submit a pull request.

## Support

If you find this project useful, please consider giving it a star on GitHub! 🌟

---

[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/users/887532157747212370)
[![X](https://img.shields.io/badge/X-%23000000.svg?style=for-the-badge&logo=X&logoColor=white)](https://twitter.com/pyriza)
