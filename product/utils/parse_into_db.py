import re
import requests
from datetime import date
from utils.validation import ProxyValidator

current_date = date.today().strftime("%Y-%m-%d")
chngsite = f"https://checkerproxy.net/api/archive/{current_date}"

list_of_sites = [
        "https://getfreeproxylists.blogspot.com",
        "http://proxysearcher.sourceforge.net/Proxy%20List.php?type=http&filtered=true",
        "http://proxysearcher.sourceforge.net/Proxy%20List.php?type=socks",
        chngsite
    ]


def get_proxies():
    res = []
    for url in list_of_sites:
        r = requests.get(url)
        result = re.findall(r'[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}', r.text)

        pv = ProxyValidator(result)
        nice_proxies = pv.run_multiproc(n_threads=10)
        res += nice_proxies
    return res
