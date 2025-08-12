<h1 align="center">
  CTG Movies Bot
</h1>

<p align="center">
  <i>A powerful and fast Telegram auto-filter bot built with Pyrogram and Motor.</i>
</p>

---

## 🌟 Features

- **🚀 Blazing Fast:** Optimized for speed and performance.
- **⚡ Powerful Auto-Filter:** Automatically filters files in groups and private messages.
- **🗂️ Multiple Database Support:** Use up to 5 MongoDB databases to store unlimited files.
- **🔐 Command-based F-Sub:** Easily add or remove Force Subscribe channels using bot commands.
  - Supports separate rules for public (must-join) and private (join-request) channels.
- **✅ Optional Verification System:** Protect your bot from spam with a user verification system.
- **🔗 Optional Link Shortener:** Integrate your favorite link shortener to earn money.
- **👤 Simple & Clean UI:** A minimal start menu for a better user experience.
- **🛠️ Admin Tools:** Essential commands for bot management like `/stats`, `/broadcast`, etc.

## 🚀 Deployment

You can easily deploy this bot to Heroku, Railway, or any VPS.

### 1. Fork the Repository

Click the "Fork" button at the top right of this page.

### 2. Set Environment Variables

You need to set the following environment variables. You can find most of them in `info.py`.

- `API_ID`: Your Telegram API ID from my.telegram.org.
- `API_HASH`: Your Telegram API Hash from my.telegram.org.
- `BOT_TOKEN`: Your bot's token from @BotFather.
- `DATABASE_1`: Your primary MongoDB connection URI.
- `DATABASE_2` (Optional)
- `DATABASE_3` (Optional)
- `DATABASE_4` (Optional)
- `DATABASE_5` (Optional)
- `ADMINS`: Your user ID (and other admin IDs, separated by spaces).
- `LOG_CHANNEL`: The ID of your private log channel.
- `CHANNELS`: The ID(s) of the channel(s) to index files from.

... and other variables as needed from `info.py`.

### 3. Deploy

[![Deploy on Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

##  commands
- `/start`: Check if the bot is alive.
- `/stats`: Get bot statistics (admins only).
- `/broadcast`: Broadcast a message to all users (admins only).
- `/addfsub`: Add a force-subscribe channel (admins only).
- `/delfsub`: Remove a force-subscribe channel (admins only).
- `/fsublist`: List all force-subscribe channels (admins only).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

- **Developer:** [Nahid/@ctgmovies23](https://t.me/ctgmovies23)
- **Framework:** [Pyrogram](https://pyrogram.org/)
