from django.conf import settings
from ipip import IPX

IPX.load(settings.IPIP_DATX_PATH)

IPX_KEYS = [
    'country', 'province', 'city', 'district',
    'isp', 'lat', 'lag',
    'timezone_name', 'timezone',
    'zip', 'phonecode', 'countrycode', 'region'
]


def query(ip, readable=False):
    data = IPX.find(ip).split('\t')
    if len(data) != 13:
        return {}
    if readable:
        return ' '.join(
            filter(bool, [data[0], data[1], data[2], data[3], data[4]])
        )
    parsed = {
        k: data[i]
        for i, k in enumerate(IPX_KEYS)
    }
    return parsed
