<br />
<div align="center" >
  <a href="https://sueeeee3.itch.io/the-worst-fishing-game-ever">
    <img width="600" height="480" alt="name" src="https://github.com/user-attachments/assets/e10e273c-1ee0-4179-8015-fe0f38a9f8a6" />
  </a>
  <br />
  <br />

  <p align="center">
    A simple, open-source Python/Pygame educational project exploring game development concepts; Made by a beginner for other beginners.
    <br />
    <h3><a href="https://sueeeee3.itch.io/the-worst-fishing-game-ever">Play it on itch!</a></h3>
  </p>
</div>


---

> **Note:** This repository contains **code only** — assets not included.
> The project is intended as a learning resource 
---
<br>

  <ol>
    <li><a href="#about-the-project">About The Project</a>
      <ul><li><a href="#built-with">Built With</a></li></ul>
    </li>
    <li><a href="#project-structure">Project Structure</a></li>
    <li><a href="#key-features">Key Features</a></li>
    <li><a href="#learning-objectives">Learning Objectives</a></li>
    <li><a href="#web-port--exe-notes">Web Port & EXE building Notes</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
  </ol>


---

# About The Project




**The Worst Fishing Game Ever** started as a school assignment in Python — and grew into a simple, open-source Pygame project built with intention of being used an educational resource for first time developers exploring game development in simple concepts. It features some simple physics, a shop and inventory system, a collectible-focused Fishpedia, and player progression mechanics with an actual ending.

The code is (still in the process of being) heavily commented, offering insight into logistics and decision making of game design; Exactly the kind of resource I wished I had when I started learning. 


<br/>

## Screenshots
<div align="center">
  <img src="https://github.com/user-attachments/assets/23a193a5-bcd1-40e0-bca0-7b6a2dbfef40" alt="Gameplay_gif" width="49%" />
  <img src="https://github.com/user-attachments/assets/7a268e0b-6f98-43b3-803c-132b3cbfc8c2" alt="Catch_screen" width="49%" />
  <img src="https://github.com/user-attachments/assets/2e70cc39-db81-4af5-bedc-d8a82bdadf30" alt="Fishpedia"    width="49%"/>
  <img src="https://github.com/user-attachments/assets/83b1fab4-785a-4e37-b74c-d2d23cfd28df" alt="Shop"         width="49%" />
</div>

<br>

### Built With

* [![Python][Python-badge]][Python-url]
* [![Pygame][Pygame-badge]][Pygame-url]
* [![Pygbag][Pygbag-badge]][Pygbag-url]

<br/>

---

## Project Structure
```
Pygame-Fishing-game/
│
├─ Desktop/
│   ├─ main.py          # Entry point for the desktop version
│   ├─ game.py          # Core game loop
│   ├─ rope.py          # Rope physics
│   ├─ fishing.py       # Rod and bait calculations
│   ├─ catch_mode.py    # Catch minigame
│   ├─ shop.py          # Shop system
│   ├─ inventory.py     # Inventory system
│   ├─ fishpedia.py     # Collectible encyclopedia
│   ├─ menus.py         # Menu screens
│   ├─ ui.py            # UI elements
│   ├─ cutscene.py      # Cutscene/Typewriter system
│   ├─ splash.py        # Splash system
│   ├─ save_system.py   # Save/load system
│   ├─ scaling.py       # Resolution scaling
│   ├─ settings.py      # Game settings
│   ├─ fish_data.py     # Fish data
│   └─ assets.py        # Assets loading
│
├─ WebPort/
│   ├─ main.py          # Entry point for the web version
│   └─ ...              # (mirrors Desktop)
│
├─ Itch_page_css            # CSS styling for the itch.io page
├─ web_loading_screen.tmpl  # Custom Pygbag loading screen template
├─ LICENSE
└─ README.md
```



---

## Key Features

- **Simple Physics** — Fake perspective of bait and splash; Dynamic rope movement; The physics behind catching minigame
- **Shop & Inventory** — Buying system with locked progress; Inventory system holding caught fish and calculating their price
- **Fishpedia** — Collectible tracking system
- **Progression Mechanics** — Player upgrades rod, unlocing new tiers and upgrades(needles cosmetics included)
- **Web Port** — Full Pygbag browser build with custom loading screen
- **Educational Codebase** — (In progress of being) Heavily commented to explain (hopefully decent) Python game development practices
- **Human-Made Code** — No AI-generated code or assets (Apologies for typos in advance)
<br/>

---

## Learning Objectives

This project is intended for new developers who want to:

- Understand how game loops and systems work in general 
- Explore basic physics and upgrade systems
- See real-world, beginner code organization for a simple 2D game
- Experiment with Pygbag for web deployment *(requires adding your own assets)*

Browse the source files directly on GitHub, or clone the repo and open it in your editor.
```sh
git clone https://github.com/Sueeeee3/Pygame-Fishing-Game.git
```

> The game cannot be run without the missing assets — this repo is for reading and learning, not executing.
<br/>


---

## Web Port & EXE Notes


> **Before anything:** This project cannot be run as-is — assets are not included in this repository.
>The commands below are written assuming Python was **not** added to PATH during installation.


### Getting started

1. **Install Python** — Download from [python.org](https://www.python.org/downloads/).

2. **Install Pygame**
```sh
   py -m pip install pygame
```

---
### Building an EXE (Windows)

1. **Install auto-py-to-exe**
```sh
   py -m pip install auto-py-to-exe
```
2. **Run it**
```sh
   py -m auto-py-to-exe
```
3. Select `main.py` as your script, choose **One Directory** mode, and click **Convert**.

> Note: You will need to manually include your assets folder and font in the auto-py-to-exe interface under "Additional Files".

---

### Building a Web Port (Pygbag)

1. **Install Pygbag**
```sh
  py -m pip install pygbag
```
2. **Run it** from your project folder
```sh
  py -m pygbag main.py 
```
Use this command to generate a build with your custom loading screen
```sh
py -m pygbag --template path/to/loadingscreen.tmpl main.py
```
3. Open your browser and go to `http://localhost:8000` to test it.

> Note: The `web/` folder in this repo shows an example of a finished Python code, ready to build, showing changes needed to make it run on web.


---

## Contributing

This project is primarily a learning resource, so contributions that help with that are most welcome — things like improving comments, fixing typos, or cleaning up code readability.

If you'd like to contribute, feel free to open an issue or submit a pull request!


---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---
<br/>
<br/>
Made with much love for game dev <3

[Python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Pygame-badge]: https://img.shields.io/badge/Pygame-000000?style=for-the-badge&logo=pygame&logoColor=white
[Pygame-url]: https://www.pygame.org/
[Pygbag-badge]: https://img.shields.io/badge/Pygbag-Web_Port-orange?style=for-the-badge
[Pygbag-url]: https://pygame-web.github.io/
