import re
import requests
from multiprocessing import Pool
from app import Proxy
from logger import log
from app import db


def isValidIp(ip):
    if ip.count('.') != 3:
        return False
    else:
        valid = True
        for i in ip.split('.'):
            try:
                if 0 <= int(i) <= 255:
                    pass
                else:
                    valid = False
            except ValueError:
                return False
        return valid


def isValidPort(port):
    valid = False
    try:
        if 0 < int(port) < 2 ** 16:
            valid = True
    except ValueError:
        return False
    return valid


def isValidProxy(proxy):
    m = re.match('^((([^:]+):([^@]+))@)?((\d{1,3}\.){3}\d{1,3})(:(\d{1,5}))?$', proxy)
    if m is None:
        return False
    ip = m.group(5)
    port = m.group(8) or '1234'

    return isValidIp(ip) and isValidPort(port)


def is_valid(proxy_server: str):
    proxy_dict = {"http": proxy_server,
                  "https": proxy_server,
                  "socks": proxy_server}
    test_site = {"http://www.google.com"}
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)'}

    for site in test_site:
        try:
            r = requests.get(site, headers=headers, proxies=proxy_dict, timeout=1)
            status = r.status_code
            if status is 200:
                return True
            else:
                return False
        except:
            return False


def check_validity():
    for proxy in Proxy.query.all():
        proxy_id = proxy.id
        try:
            is_valid_proxy = is_valid(proxy_server=proxy.ip + ':' + proxy.port)
            if isinstance(is_valid_proxy, bool):
                db.session.query(Proxy).filter(Proxy.id == proxy_id).update({Proxy.is_valid: is_valid_proxy})
                db.session.commit()
        except Exception as e:
            log("Error while checking validity: " + str(e))
            pass
    log("Checked validity")


class ProxyValidator:
    def __init__(self, url_list):
        self.url_list = url_list

    def iter_proxies(self, urls):
        for p in urls:
            yield p

    def check_proxies(self, proxy):
        return isValidProxy(proxy) and is_valid(proxy)

    def get_valid_proxy(self, proxy):
        return proxy if isValidProxy(proxy) and is_valid(proxy) else None

    def multiproc(self, iterator_input, function, n_threads):
        with Pool(n_threads) as pool:
            iterator_output = pool.imap(function, iterator_input)
            for obj in iterator_output:
                yield obj

    def run_proc(self):
        iterator_input = self.iter_proxies(self.url_list)
        iterator_output = filter(self.check_proxies, iterator_input)
        valid_proxies = list(iterator_output)
        return valid_proxies

    def run_multiproc(self, n_threads=10):
        iterator_input = self.iter_proxies(self.url_list)
        iterator_output = self.multiproc(iterator_input, self.get_valid_proxy, n_threads)
        return [p for p in iterator_output if p]
