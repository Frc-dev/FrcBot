# osu! lazer Recommendation Bot

This is a bot that recommends maps based on your top plays. You can either:

- **Run it locally** by downloading the source code and running:

    ```
    python localClient.py
    ```

    Make sure you have all the [requirements to run locally](https://github.com/Frc-dev/FrcBot/tree/master?tab=readme-ov-file#%EF%B8%8F-requirements-to-run-locally) set up before starting the bot.

- **Use it in-game** by sending a DM to [**Frc**](https://osu.ppy.sh/users/4638940) in osu!  
  > _Note: If you don't receive a response, DM the bot to let me know and I will read it, the bot should be hosted in a server and working 24/7._

---

## Features

- `!r` — Recommends you a map based on your top plays.
- `!r [mod]` — Recommends you a map based on your top plays with the mod of your choice.
- `!settings [mods] [acc]` — Change your preferences for recommendations.
  - Example: `!settings acc 98`
- `!settings acc [95, 98, 100]` — Recommends maps where your chosen accuracy will yield positive results. Default is 98.
- `!settings mods` — Displays currently banned mods.
- `!settings mods [NM, HD, HR, HDHR, HDDT, HRDT, HDHRDT]` — Toggle mod combinations to exclude from recommendations. You can set them individually or in HD, HDHR, HRDT format to toggle several at once. By default HRDT and HDHRDT are banned.
- `!settings user [username|userid|0]` — Set a custom user to get recommendations for, 0 will clear the current user and use yours instead.
- `!settings algo [farm|all]` — Set the bots algorithm, do you want to use the bot for farming? Or you don't mind being recommended non-farm maps? By default you're put into the farm algorithm.
- `!feedback [message]` - Talk to me directly, report bugs, provide suggestions. Way easier for me to read your message and the feedback is much appreciated.
- `!help` - Get a list of the commands you can use.

> _The bot uses the **osu! v2 API**, so it includes your lazer plays and returns lazer pp values._

---

## TODO

- [ ] Automate map processing
- [ ] Add a new acc_99 setting
- [ ] Add /np command with !with options
- [ ] Allow setting to set custom pp baseline

---

## Requirements to Run Locally

- Python 3.8+ and `sqlite3`
- A SQLite database
- The following Python packages:
  - `rosu-pp-py`
  - `ossapi`
  - `requests`
  - `dotenv`
  - `irc`

Install the dependencies with:

```bash
pip install rosu-pp-py ossapi requests python-dotenv irc
```
### Setup Instructions

Once the source code is downloaded, you'll need to configure a few things before running the bot.

#### 1. Create a `.env` file

In the root directory, create a file named `.env` with the following content:

```env
OSU_CLIENT_ID=""
OSU_CLIENT_SECRET=""
OSU_IRC_USERNAME=""
OSU_IRC_PASSWORD=""
SONGS_ROOT_DIR=""
```

`OSU_CLIENT_ID` and `OSU_CLIENT_SECRET` are needed to interact with the v2 API, you can get the credentials [here, by creating a new OAuth Application](https://osu.ppy.sh/home/account/edit).

`OSU_IRC_USERNAME` and `OSU_IRC_PASSWORD` are only required if you plan to run `ircClient.py` to host your own online bot (totally fine as long as you give credit).

`SONGS_ROOT_DIR` should be the path to your local Songs folder (ideally from osu!stable), which `insertData.py` uses to find `.osu` files for populating the database.

#### 2. Populate the Database

From the project root, run:

```bash
python insertData.py
```

This will scan the specified Songs directory and populate your SQLite database.


#### 3. Start the Bot

You can now choose how you want to run the bot:

- To start the **Bancho bot (IRC-based)**:

  ```bash
  python ircClient.py
  ```

- To start the **local CLI bot (command line)**:

  ```bash
  python localClient.py
  ```
  
If anything is unclear or you're stuck, feel free to reach out!

---

## Credits

- [rosu-pp-py](https://github.com/4nykey/rosu-pp-py) — For performance point calculation
- [ossapi](https://github.com/ppy/ossapi) — osu! v2 API wrapper
