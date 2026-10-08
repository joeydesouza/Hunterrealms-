# Hunter Realms

A mobile-first online RPG in the classic top-down MMO style, with a built-in hunt
assistant (auto heal, mana, attack, spell rotation). Android first.

| Part | What it is |
|---|---|
| `server/` | Game server: [Canary](https://github.com/opentibiabr/canary) engine (GPL-2.0, pinned in `VERSIONS`) + our datapack `data-hunterrealms`, config and core overrides |
| `client/` | Overlay applied on top of [OTClient](https://github.com/mehah/otclient) (MIT, pinned): our assets, login URL, branding, and the `hr_assistant` bot mod |
| `web/` | Node/Express login + sign-up service (the client's HTTP login protocol, argon2 passwords) |
| `assets/` | Source art (CC0, Dungeon Crawl Stone Soup tiles) + `manifest.json` listing every item, outfit, effect and missile |
| `tools/` | `assetc` (PNG → client/server asset files), `mapgen` (world, items.xml, monsters) |

Everything derived is regenerated with `tools/build_all.sh` (needs `pip install grpcio-tools pillow`).

## Play on your phone (home Wi-Fi)

You need: this PC with Docker Desktop running, and the phone on the same Wi-Fi.

1. **Find your PC's address.** In PowerShell run `ipconfig` and copy the **IPv4 Address**
   of your Wi-Fi/Ethernet adapter (looks like `192.168.1.50`).
2. **Configure.** In this folder copy `.env.example` to `.env` and set `GAME_HOST=` to that
   address. Change both passwords.
3. **Start the server.** In this folder run `docker compose up -d --build`.
   The first build compiles the engine and takes 30–60 minutes; later starts take seconds.
   Check it with `docker compose logs -f server` until you see `Hunter Realms server online!`
4. **Open the firewall.** Allow inbound TCP **7171, 7172, 8080** on Windows Firewall
   (Windows Security → Firewall → Advanced settings → Inbound Rules → New Rule → Port).
5. **Create your account.** On the phone's browser open `http://<your IP>:8080` and sign up.
6. **Build the app.** On GitHub: **Actions → Android APK → Run workflow**, login URL
   `http://<your IP>:8080/login`, port `8080`. It takes about an hour. When it finishes,
   download the `hunterrealms-apk` artifact.
7. **Install.** Unzip, copy the `.apk` to the phone, open it, and allow
   "Install unknown apps" when Android asks.
8. **Play.** Log in with your email and password. Use the joystick to walk; the buttons
   on the right of the map are the hunt assistant (Heal / Mana / Attack / Spells / Setup).

If your PC's IP changes, rebuild the APK with the new address (step 6), or reserve the IP
in your router.

## Development notes

* Our content ids live at **60000+** (grounds 60100, walls 60200, nature 60300, doors
  60400, items 61000+). Ids the engine hard-codes (coins 3031/3035/3043, backpack 2854,
  depot/inbox containers, corpses, splashes) keep their engine numbers with our art.
* All 303 magic effects and 62 missiles exist (placeholder art) because the engine sends
  them by number; a missing id breaks the client's packet parsing.
* Login goes through `web/` (`POST /login`); the game world is on 7172.
* Tests: `cd web && npm test`.

## Before going public

* Replace OTClient's default UI art and login background (they come from upstream and
  include Tibia-styled graphics) with our own.
* Swap placeholder effect art and the one-direction creature sprites for proper art.
* Put the login service behind HTTPS and move the server to a host (e.g. AWS).
* Canary is GPL-2.0: if we distribute server binaries, publish our server changes.
