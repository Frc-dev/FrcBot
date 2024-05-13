# osu! lazer Recommendation Bot

This is a bot that recommends maps based on your top plays. You can either:

- **Run it locally** by downloading the source code and running:

    ```
    python localClient.py
    ```

- **Use it in-game** by sending a DM to **Frc** in osu!  
  > _Note: If you don't receive a response, my computer might be off or the bot isn't running. Feel free to DM me to let me know._

---

## 💡 Features

- `!r` — Recommends you a map based on your top plays.
- `!settings [banned_mods] [acc_preference]` — Change your preferences for recommendations.
  - Example: `!settings acc_preference 98`
- `!settings acc_preference [95, 98, 100]` — Recommends maps where your chosen accuracy will yield positive results. Default is 98.
- `!settings banned_mods` — Displays currently banned mods.
- `!settings banned_mods [NM, HD, HR, HDHR, HDDT, HDDTHR]` — Toggle mod combinations to exclude from recommendations.

> _The bot uses the **osu! v2 API**, so it includes your lazer plays and returns lazer pp values._

---

## 📋 TODO

- [ ] Improve this README
- [ ] Post full instructions on how to build and run locally
- [ ] Fix settings not being saved
- [ ] Normalize mod formatting (e.g., `HD+HR` → `HDHR`)
- [ ] Allow banning multiple mods at once (no need to send the command repeatedly)
- [ ] Host the bot on a server so it's available 24/7

---

## ⚙️ Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`
- osu! v2 API credentials

---

## 🧠 Credits

- [rosu-pp-py](https://github.com/4nykey/rosu-pp-py) — For performance point calculation
- [ossapi](https://github.com/ppy/ossapi) — osu! v2 API wrapper
