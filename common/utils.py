import base64
import functools
from operator import itemgetter
from itertools import groupby
import os
import pickle
from datetime import datetime, timedelta
from typing import Union
# import pandas as pd


# logging.debug('This is a debug message')
# logging.info('This is an info message')
# logging.warning('This is a warning message')
# logging.error('This is an error message')
# logging.critical('This is a critical message')


ConvertibleTimestamp = Union[datetime, str]


def remember_me(user, path):
    with open(path, 'bw') as file:
        pickle.dump(user, file)


def base64_converter(img):
    return base64.b64encode(img).decode("utf8")


def get_me(path):
    if os.path.exists(path):
        with open(path, 'rb') as file:
            user = pickle.load(file)
        if user:
            return user
        else:
            return None
    else:
        return None


def check_if_midnight():
    now = datetime.now()
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return seconds_since_midnight == 0


def id_filter(pid, lst, compare=None):  # do we need this ?
    if compare == 'pid':
        return list(filter(lambda x: x.project_id == pid, lst))
    return list(filter(lambda x: x.id == pid, lst))


def group_by_and_accumulate_timedelta_list_of_tuples(lst) -> dict:
    it = groupby(lst, itemgetter(0))
    items = {}
    for key, subiter in it:
        durations = list(item[1] for item in subiter)
        items[key] = sum(durations, timedelta())
    return items


def extract_before_from(text: str, find: str):
    return text[:text.find(find) + len(find)]


# def create_df_from_object(obj):
#     df = pd.DataFrame(obj).T
#     df.columns = df.iloc[0]
#     df = df.drop(0, ).reset_index(drop=True)
#     return df


# def calculate_internet_speed():
#     internet = speedtest.Speedtest()
#     return internet.download(), internet.upload()


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        x = func(*args, **kwargs)
        end = time.time()
        print(f'{func.__name__} Took {end - start} Time to excute')
        return x

    return wrapper


def get_network_info():
    from typing import Tuple, List
    from socket import AF_LINK, AF_INET, AF_INET6
    import psutil

    class NetworkInterfaceNotFound(Exception):
        pass

    def get_active_nets():
        """
        Get active NIC names.

        Returns:
            Set of active NIC names.
        """

        return {name for name, net in psutil.net_if_stats().items() if net.isup}

    def determine_current_nic(*net_names) -> Tuple[str, str, List[str], List[str]]:
        """
        Determine primary active NIC.

        Notes:
            One NIC may have multiple addresses of same family. Thus returning in list.

        Args:
            *net_names: NIC names to look for. NIC priority == item order

        Returns:
            NIC's Name, MAC, IPv4 address list, IPv6 address list
        """

        types = {
            AF_LINK.name: [],
            AF_INET.name: [],
            AF_INET6.name: [],
        }

        active_nets = get_active_nets()
        address_dict = psutil.net_if_addrs()
        print(active_nets, address_dict)
        matching_name = ""

        for net_name in net_names:
            if net_name in active_nets:
                # now we have the device.
                matching_name = net_name
                break

        else:
            # if none exists, raise
            raise NetworkInterfaceNotFound(f"There's no matching NIC with names {net_names}")

        for address in address_dict[matching_name]:
            types[address.family.name].append(address.address)

        return matching_name, types[AF_LINK.name][0], types[AF_INET.name], types[AF_INET6.name]
        # otherwise, no matching NIC

    name_, mac, ipv4, ipv6 = determine_current_nic()
    print(name_, mac, ipv4, ipv6)

if __name__ == "__main__":
    # import psutil
    # from pprint import pprint
    #
    # nets = psutil.net_if_stats()
    # pprint(nets)
    #
    # nets = psutil.net_if_addrs()
    # pprint(nets)

    get_network_info()
    pass
