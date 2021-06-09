import requests
import json
import os
import time
from itertools import cycle
from threading import Thread
import random

from proxies import proxy
import default

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}
# session = requests.session()
# session.headers["User-Agent"] = ""

self = None


def clear():
    os.system("cls" if os.name == "nt" else "clear")


class steam:
    def __init__(self):
        self.config = default.get()
        self.debug = self.config.debug_steam
        self.proxy_error = 0
        self.delay_error = 60 * 0.5  # 5
        self.game_data_got = 0
        self.current_game_id = 0
        try:
            self.total_num_games = len(
                self.read_json(self.store_data_json)["applist"]["apps"]["app"]
            )
        except:
            self.total_num_games = 0
        self.proxies = proxy(self.debug)
        # self.proxies = []
        self.proxy_len = len(self.proxies)
        self.proxy_pool = cycle(self.proxies)
        self.current_loc = os.path.dirname(__file__)
        self.steam_loc = os.path.join(self.current_loc, "data")
        self.store_data_json = os.path.join(self.steam_loc, "store_data.json")
        self.price_data_json = os.path.join(self.steam_loc, "price_data.json")
        self.all_data_json = os.path.join(self.steam_loc, "id")
        self.free_game_data_json = os.path.join(
            self.steam_loc, "free_game_data.json")
        self.price_data_dict = {}
        self.all_data_dict = {}
        self.free_game_data_dict = {}
        self.threads = []
        self.session = requests.session()

    def debug_print(self, obj):
        if self.debug:
            print(obj)

    def add_game_data_got(self):
        self.game_data_got += 1

    def add_proxy_error(self):
        self.debug_print("Add Proxy Error Count")
        self.proxy_error += 1

    def reset_proxy_error(self):
        self.proxy_error = 0

    def all_data_screen(self, version):
        if not self.debug:
            if version == 0:
                clear()
                print(
                    f"Number of Proxies Used : {self.proxy_len}\n\nCurrent Proxy Error Count : {self.proxy_error}\n\nDelay Error Set To : {self.delay_error / 60} Minutes\n\nNumber of Games Gotten : {self.game_data_got}\n\nTotal Number of Games : {self.total_num_games}\n\nPercentage Complete : {self.game_data_got / self.total_num_games}\n\nCurrent Game ID : {self.current_game_id}"
                )

    def game_data_reset(self):
        self.game_data_got = 0
        self.current_game_id = 0

    def read_json(self, path):
        f = open(
            path,
        )
        json_data = json.load(f)
        return json_data

    def write_json(self, path, data):
        with open(path, "w") as file:
            json.dump(data, file, indent=4)
        return

    def get_url_json(self, url):
        try:
            # rand_proxy = random.choice(self.proxies)
            # proxy = {"http": rand_proxy, "https": rand_proxy}
            # response = session.get(url, proxies=proxy, timeout=20)
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                self.debug_print(
                    f"Response Status Code: {response.status_code}")
                raise Exception()
            self.debug_print(url)
            self.reset_proxy_error()
        except Exception as e:
            self.add_proxy_error()
            if self.proxy_len == 0:
                self.debug_print("Sleeping")
                time.sleep(self.delay_error)
            elif self.proxy_error % self.proxy_len == 0:
                if self.debug:
                    print("Sleeping")
                time.sleep(self.delay_error)
                self.reset_proxy_error()
            self.debug_print(e)
            if self.proxy_len != 0:
                proxy = next(self.proxy_pool)
                self.session.proxies.update({"http": proxy, "https": proxy})
            self.get_url_json(url)
        else:
            return response.json()

    def get_store_data(self):
        url = "http://api.steampowered.com/ISteamApps/GetAppList/v0001/"
        self.write_json(self.store_data_json,
                        self.session.get(url, timeout=20).json())
        self.total_num_games = len(
            self.read_json(self.store_data_json)["applist"]["apps"]["app"]
        )
        return

    def get_price_data(self):
        def get_price_data_in_batch(id_data):
            id_str = ""
            for id in id_data:
                id_str += str(id["appid"]) + ","
            price_url = f"https://store.steampowered.com/api/appdetails?appids={id_str}&cc=us&filters=price_overview"
            data_json = self.get_url_json(price_url)
            try:
                self.price_data_dict.update(data_json)
                self.debug_print(id_str)
            except Exception as e:
                self.debug_print(e)
                get_price_data_in_batch(id_data)
            return

        app_list = self.read_json(self.store_data_json)[
            "applist"]["apps"]["app"]
        for id in range(0, len(app_list), 1000):
            get_price_data_in_batch(list(app_list)[id: id + 1000])
        self.write_json(self.price_data_json, self.price_data_dict)
        self.game_data_reset()
        return

    def get_all_data(self):
        def get_single_data(id_str):
            data_url = (
                f"https://store.steampowered.com/api/appdetails?appids={id_str}&cc=US"
            )
            data_json = self.get_url_json(data_url)
            try:
                self.all_data_dict.update(data_json)
                self.write_json(
                    os.path.join(self.all_data_json,
                                 id_str + ".json"), data_json
                )
                self.debug_print(id_str)
            except Exception as e:
                self.debug_print(e)
                get_single_data(id_str)
            return

        if default.dateint() == int(self.config.steam_all_data):
            # app_list = self.read_json(self.store_data_json)["applist"]["apps"]["app"]
            # self.total_num_games = len(app_list)

            # for id in range(0, len(app_list)):
            #     get_single_data(str(app_list[id]["appid"]))

            # ### Threading
            app_list = self.read_json(self.store_data_json)[
                "applist"]["apps"]["app"]
            for id in range(0, len(app_list)):
                thread = Thread(
                    target=get_single_data, args=(str(app_list[id]["appid"]),)
                )
                thread.start()
                self.threads.append(thread)

            for thread in self.threads:
                thread.join()
            # ###
            # self.write_json(self.all_data_json, self.all_data_dict)
            self.game_data_reset()
        return

    def get_free_games(self):
        price_dict = self.read_json(self.price_data_json)

        for key, value in price_dict.items():
            try:
                if value["data"]["price_overview"]["discount_percent"] == 100:
                    self.free_game_data_dict.update(
                        {
                            key: self.get_url_json(
                                f"https://store.steampowered.com/api/appdetails?appids={key}&cc=US"
                            )
                        }
                    )
            except Exception as e:
                self.debug_print(e)
                pass

        self.write_json(self.free_game_data_json, self.free_game_data_dict)
        return


print("Getting Proxy Data")
steam_item = steam()
# clear()
print("Getting Store Data")
steam_item.get_store_data()
# # clear()
print("Getting Price Data")
steam_item.get_price_data()
# clear()
# print("Getting All Data")
# steam_item.get_all_data()
# clear()
print("Getting Free Games")
steam_item.get_free_games()
