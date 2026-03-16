import json
import os
#Got rid of mouse sensitivity saving since it doesnt work on web

try: #Check if web version or not
    from platform import window  
    WEB = True
except ImportError:
    WEB = False

STORAGE_KEY = "fishing_game_save" #Local storage name


class SaveSystem:
    def __init__(self, path="save.json"):
        self.path = path

    def _to_dict(self, game): #Saving into Local storage if web
        shop = game.shop
        return {
            "money":             game.money,
            "inventory_tier":    game.inventory.tier,
            "inventory_items":   game.inventory.items,
            "rod_tier":          shop.rod_tier,
            "rod_cosmetic":      shop.rod_cosmetic,
            "tier2_upgraded":    shop.tier2_upgraded,
            "tier3_upgraded":    shop.tier3_upgraded,
            "rod_owned":         [r["owned"] for r in shop.rod_items],
            "inv_owned":         [i["owned"] for i in shop.inventory_items],
            "upg_owned":         [u["owned"] for u in shop.upgrade_items],
            "caught_fish":       game.fishpedia.caught_fish,
            "seen_events":       list(game.seen_events),
            "mouse_sensitivity": game.mouse_sensitivity,
            "music_volume":      game.music_volume,
        }

    def save(self, game):
        data = self._to_dict(game)
        if WEB:
            window.localStorage.setItem(STORAGE_KEY, json.dumps(data)) #Saving into Local Storage if web
        else:
            with open(self.path, "w") as f:
                json.dump(data, f, indent=4)

    def _read_data(self): #Added reading data so it works with web and not and in both cases loads the same way
        if WEB:
            raw = window.localStorage.getItem(STORAGE_KEY) #Read Local Storage
            if raw is None:
                return None
            return json.loads(raw)
        else:
            if not os.path.exists(self.path):
                return None
            with open(self.path, "r") as f:
                return json.load(f)

    def load(self, game):
        data = self._read_data()
        if data is None:
            return False

        shop = game.shop
        game.money           = data["money"]
        game.inventory.tier  = data["inventory_tier"]
        game.inventory.items = data["inventory_items"]

        shop.rod_tier       = data.get("rod_tier", 1)
        shop.rod_cosmetic   = {int(k): v for k, v in data.get("rod_cosmetic", {1: "default", 2: "default", 3: "default"}).items()}
        shop.tier2_upgraded = data["tier2_upgraded"]
        shop.tier3_upgraded = data["tier3_upgraded"]

        for i, owned in enumerate(data.get("rod_owned", [])):
            if i < len(shop.rod_items):
                shop.rod_items[i]["owned"] = owned
        shop.max_rod_tier = shop._max_unlocked_tier()

        for i, owned in enumerate(data.get("inv_owned", [])):
            if i < len(shop.inventory_items):
                shop.inventory_items[i]["owned"] = owned

        for i, owned in enumerate(data.get("upg_owned", [])):
            if i < len(shop.upgrade_items):
                shop.upgrade_items[i]["owned"] = owned

        game.fishpedia.caught_fish = data.get("caught_fish", {})
        game.seen_events           = set(data.get("seen_events", []))
        game.music_volume          = data.get("music_volume", 1.0)
        return True

    def reset(self, game): #Added web case, reset local data and set defalut values
        if WEB:
            window.localStorage.removeItem(STORAGE_KEY)
        elif os.path.exists(self.path):
            os.remove(self.path)

        shop = game.shop
        shop.rod_tier       = 1
        shop.max_rod_tier   = 1
        shop.tier2_upgraded = False
        shop.tier3_upgraded = False
        shop.open           = False
        shop.rod_scroll     = 0
        shop.rod_cosmetic   = {1: "default", 2: "default", 3: "default"}

        for rod in shop.rod_items:
            rod["owned"] = rod["tier"] == 1 and rod["variant"] == "default"
        for inv in shop.inventory_items:
            inv["owned"] = inv["tier"] == 1
        for upg in shop.upgrade_items:
            upg["owned"] = upg["flag"] is None

        game.inventory.items  = []
        game.inventory.scroll = 0
        game.inventory.tier   = 1
        game.money            = 0
        game.music_volume     = 1.0
        game.fish_added                 = False
        game.fishpedia.caught_fish      = {}
        game.seen_events                = set()
        game.cutscene                   = None
        game.special_splash_active      = False

    def has_save(self): #Added web support
            if WEB:
                return window.localStorage.getItem(STORAGE_KEY) is not None
            return os.path.exists(self.path)

    def load_settings_only(self, game): 
        data = self._read_data()
        if data is None:
            return
        game.music_volume = data.get("music_volume", 1.0)
