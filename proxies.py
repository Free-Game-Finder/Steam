import requests
import pandas as pd
import re
import base64

import socket
from threading import Thread

socket.setdefaulttimeout(30)

proxy_list_url = [
    "https://free-proxy-list.net/",
    "https://www.sslproxies.org/",
    "https://www.us-proxy.org/",
    "https://free-proxy-list.net/anonymous-proxy.html",
]

threads = []
working_proxy = []


def get_proxies_1():
    proxy_list = []
    for proxy_url in proxy_list_url:
        resp = requests.get(proxy_url)
        df = pd.read_html(resp.text)[0]
        df = df[(df["Https"] == "yes")]
        df["Proxy Address"] = df["IP Address"].map(
            str) + ":" + df["Port"].map(str)
        proxy_list += df["Proxy Address"].values.tolist()
    return [proxy.rsplit(".", 1)[0] for proxy in proxy_list]


def get_proxies_2():
    def decodeBase64(address):
        substring = re.search(r'"([^"]*)"', address).group(1)
        return (base64.b64decode(substring)).decode("utf-8")

    resp = requests.get(
        "http://free-proxy.cz/en/proxylist/country/all/https/ping/all")
    df = pd.read_html(resp.text)[1]
    df = df[~df.Port.str.contains("adsbygoogle")]
    df["clean_address"] = df.apply(
        lambda row: decodeBase64(row["IP address"]), axis=1)
    df["Proxy Address"] = df["clean_address"].map(
        str) + ":" + df["Port"].map(str)
    return df["Proxy Address"].values.tolist()


def get_proxies_3():
    def clean(address):
        address = str(address)
        try:
            return re.findall(r"'(.*?)'", address, re.DOTALL)[0]
        except:
            pass

    resp = requests.get("https://www.proxynova.com/proxy-server-list/")
    df = pd.read_html(resp.text)[0]
    df["ProxyIP"] = df["Proxy IP"]
    df = df[~df.ProxyIP.str.contains("adsbygoogle", na=False)]
    df["clean_address"] = df.apply(lambda row: clean(row["Proxy IP"]), axis=1)
    df["Proxy Address"] = df["clean_address"].map(
        str) + ":" + df["Proxy Port"].map(str)
    proxy_list = df["Proxy Address"].values.tolist()
    return [
        proxy
        for proxy in proxy_list
        if not any(ignore in proxy for ignore in ["None", "nan"])
    ]


def get_proxies_4():
    resp = requests.get("https://scrapingant.com/free-proxies/")
    df = pd.read_html(resp.text)[0]
    # df = df[(df["Country"] == "🇺🇸 United States")]
    df["Proxy Address"] = df["IP"].map(str) + ":" + df["Port"].map(str)
    return df["Proxy Address"].values.tolist()


def get_proxies_5():
    free_proxies = []
    for reqnum in range(20):
        try:
            resp = requests.get(
                "https://api.getproxylist.com/proxy?country=US&allowsHttps=1&maxConnectTime=5"
            ).json()
            free_proxies.append(resp["ip"] + ":" + str(resp["port"]))
        except:
            pass
    return free_proxies


def get_proxies_6():
    free_proxies = []
    for reqnum in range(10):
        try:
            resp = requests.get(
                "https://gimmeproxy.com/api/getProxy?get=true&supportsHttps=true&protocol=http"
            ).json()
            free_proxies.append(resp["ipPort"])
        except:
            pass
    return free_proxies


def get_proxies_7():
    resp = requests.get(
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
    ).text
    proxies = []
    for proxy in resp.split("\n"):
        if proxy != "":
            proxies.append(proxy)
    return proxies


def get_proxies_8():
    resp = requests.get(
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    ).text
    proxies = []
    for proxy in resp.split("\n"):
        if proxy != "":
            proxies.append(proxy)
    return proxies


def get_proxies_9():
    resp = requests.get(
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt"
    ).text
    proxies = []
    for proxy in resp.split("\n"):
        if proxy != "":
            proxies.append(proxy)
    return proxies


def get_proxies_10():
    resp = requests.get(
        "https://raw.githubusercontent.com/chipsed/proxies/main/proxies.txt"
    ).text
    proxies = []
    for proxy in resp.split("\n"):
        if proxy != "":
            proxies.append(proxy)
    return proxies


def get_proxies_11():
    resp = requests.get(
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt"
    ).text
    proxies = []
    for proxy in resp.split("\n"):
        if proxy != "":
            proxies.append(proxy)
    return proxies


def get_proxies_12():
    resp = requests.get(
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
    ).text
    proxies = []
    for proxy in resp.split("\n"):
        if proxy != "":
            proxies.append(proxy)
    return proxies


def get_proxies_13():
    resp = requests.get(
        "https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.json"
    ).json()
    proxies = []
    for proxy in resp["proxies"]:
        proxies.append(proxy["ip"] + ":" + proxy["port"])
    return proxies


def get_proxies_14():
    resp = requests.get(
        "https://www.proxy-list.download/api/v1/get?type=https").text
    proxies = []
    for proxy in resp.split("\n"):
        if proxy != "":
            proxies.append(proxy.replace("\r", ""))
    return proxies


def get_proxies_15():
    resp = requests.get(
        "https://www.proxy-list.download/api/v1/get?type=http").text
    proxies = []
    for proxy in resp.split("\n"):
        if proxy != "":
            proxies.append(proxy.replace("\r", ""))
    return proxies


def get_proxies(debug=False):
    unchecked_proxies = []
    try:
        unchecked_proxies += get_proxies_1()
    except Exception as e:
        if debug:
            print(e)
    try:
        unchecked_proxies += get_proxies_2()
    except Exception as e:
        if debug:
            print(e)
    try:
        unchecked_proxies += get_proxies_3()
    except Exception as e:
        if debug:
            print(e)
    try:
        unchecked_proxies += get_proxies_4()
    except Exception as e:
        if debug:
            print(e)
    try:
        unchecked_proxies += get_proxies_5()
    except Exception as e:
        if debug:
            print(e)
    try:
        unchecked_proxies += get_proxies_6()
    except Exception as e:
        if debug:
            print(e)
    try:
        unchecked_proxies += get_proxies_7()
    except Exception as e:
        if debug:
            print(e)
    try:
        unchecked_proxies += get_proxies_8()
    except Exception as e:
        if debug:
            print(e)
    try:
        unchecked_proxies += get_proxies_9()
    except Exception as e:
        if debug:
            print(e)
    try:
        unchecked_proxies += get_proxies_10()
    except Exception as e:
        if debug:
            print(e)
    try:
        unchecked_proxies += get_proxies_11()
    except Exception as e:
        if debug:
            print(e)
    try:
        unchecked_proxies += get_proxies_12()
    except Exception as e:
        if debug:
            print(e)
    try:
        unchecked_proxies += get_proxies_13()
    except Exception as e:
        if debug:
            print(e)

    return unchecked_proxies


def check_proxy(proxy, debug=False):
    try:
        print(len(working_proxy))
        stat = requests.get(
            "https://store.steampowered.com/api/appdetails?appids=675357,675358,675359,675360,675370,675390,675400,675410,675420,675430,675490,675500,675510,675520,675530,675560,675590,675600,675620,675630,675640,675650,675660,675690,675720,675730,675750,675770,675780,675790,675800,675801,675030,675040,675060,675080,675090,675091,675092,675093,675094,675095,675096,675097,675098,675099,675100,675101,675120,675130,675140,675150,675151,675152,675160,675170,675180,675190,675200,675210,675220,675230,675240,675250,675260,675270,675280,675290,675330,675340,675350,675351,675354,675355,674530,674550,674560,674570,674580,674590,674630,674670,674700,674720,674730,674750,674760,674780,674800,674840,674850,674880,674890,674900,674910,674920,674940,674950,674960,674970,674980,675010,674070,674080,674100,674120,674130,674160,674170,674180,674190,674200,674210,674220,674230,674240,674250,674290,674300,674310,674320,674330,674360,674370,674380,674390,674400,674420,674430,674440,674450,674460,674480,674500,674520,673530,673540,673550,673560,673570,673580,673590,673600,673620,673630,673660,673690,673710,673720,673730,673790,673800,673810,673820,673830,673840,673850,673870,673890,673900,673920,673930,673940,673950,673970,673990,674000,674010,673030,673040,673050,673060,673070,673080,673090,673120,673130,673140,673170,673190,673210,673220,673230,673250,673260,673270,673280,673300,673310,673320,673340,673360,673380,673400,673410,673430,673440,673480,673500,672560,&cc=us&filters=price_overview",
            proxies={"http": proxy, "https": proxy},
            timeout=10,
        )
        if stat.status_code == 200:
            working_proxy.append(proxy)
    except Exception as e:
        if debug:
            print(e)
        return e
    return


def proxy(debug):
    unstable_proxies = get_proxies(debug)

    for proxy in unstable_proxies:
        thread = Thread(target=check_proxy, args=(proxy, debug))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return working_proxy
