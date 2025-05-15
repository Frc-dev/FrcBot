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

## 💡 Features

- `!r` — Recommends you a map based on your top plays.
- `!settings [banned_mods] [acc_preference]` — Change your preferences for recommendations.
  - Example: `!settings acc_preference 98`
- `!settings acc_preference [95, 98, 100]` — Recommends maps where your chosen accuracy will yield positive results. Default is 98.
- `!settings banned_mods` — Displays currently banned mods.
- `!settings banned_mods [NM, HD, HR, HDHR, HDDT, HRDT, HDHRDT]` — Toggle mod combinations to exclude from recommendations. You can set them individually or in HD, HDHR, HRDT format to toggle several at once

> _The bot uses the **osu! v2 API**, so it includes your lazer plays and returns lazer pp values._

---

## 📋 TODO

- [x] Improve this README
- [x] Post full instructions on how to build and run locally
- [x] Fix settings not being saved
- [x] Normalize mod formatting (e.g., `HD+HR` → `HDHR`)
- [x] Allow banning multiple mods at once (no need to send the command repeatedly)
- [x] Host the bot on a server so it's available 24/7
- [ ] Fix users not receiving correct format list of mods after setting them wrong
- [ ] Add command to provide feedback to me directly
- [ ] Rewrite beatmap lookup so it works with osu direct
- [ ] Handle really old map recommendations returning non-usable download links
- [ ] Handle some beatmaps returning -1 for its beatmapset id
- [ ] Allow setting to set specific user you want the recommendations to pull from
- [ ] Allow setting to set custom pp baseline
- [ ] Add option to !r with a specific mod
- [ ] Find a way to keep the database updated as new maps are ranked

---

## ⚙️ Requirements to Run Locally

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
### 🛠️ Setup Instructions

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

## 🧠 Credits

- [rosu-pp-py](https://github.com/4nykey/rosu-pp-py) — For performance point calculation
- [ossapi](https://github.com/ppy/ossapi) — osu! v2 API wrapper
