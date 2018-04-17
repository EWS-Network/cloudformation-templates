#!/usr/bin/env python

"""
POC for subnet calculator
"""

import ipaddress
import base64
import json
import random
import string
import hashlib
import uuid
import httplib
import urlparse
import boto3
from math import (
    log,
    ceil
)

pow2_2_prefix = {

    '16': 28,
    '32': 27,
    '64': 26,
    '128': 25,
    '256': 24,
    '512': 23,
    '1024': 22,
    '2048': 21,
    '4096': 20,
    '8192': 19,
    '16384': 18,
    '32768': 17,
    '65536': 16,
    '131072': 15,
    '262144': 14,
    '524288': 13,
    '1048576': 12,
    '2097152': 11,
    '4194304': 10,
    '8388608': 9,
    '16777216': 8
}

clpow2 = lambda x: pow(2, int(log(x, 2) + 0.5))
nxtpow2 = lambda x: int(pow(2, ceil(log(x, 2))))




def cut_per_az(az_cidr, layers_cidr):
    """
    """

    maj_splits = list(az_cidr.subnets(prefixlen_diff=1))
    layers_cidr['app'].append(maj_splits[0])
    min_splits = list(maj_splits[1].subnets(prefixlen_diff=1))
    layers_cidr['pub'].append(min_splits[0])
    layers_cidr['stor'].append(min_splits[1])


def get_subnets(cidr, azs):
    """
    Main function
    """
    cidr = unicode(cidr)
    vpc_net = ipaddress.IPv4Network(cidr)
    number_ips = int(vpc_net.num_addresses - 2)

    if (azs != 2) and (azs % 2):
        azs += 1

    layers_cidr = {
        'app' : [],
        'pub': [],
        'stor': []
    }

    ips_per_az = number_ips / azs
    pow2 = clpow2(ips_per_az)
    azs_prefix = pow2_2_prefix['%d' % (pow2)]
    subnets_per_az = list(vpc_net.subnets(new_prefix=azs_prefix))

    for az in subnets_per_az:
        cut_per_az(az, layers_cidr)

    return layers_cidr



if __name__ == '__main__':

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Splits a CIDR to generate VPC subnets")
    parser.add_argument("--cidr", help="CIDR", required=True)
    parser.add_argument("--azs", help="AZs", required=True)

    args = parser.parse_args()

    layers = get_subnets(args.cidr, int(args.azs))

    cidrs = {}

    for layer in layers:
        cidrs[layer] = []
        sub_list = []
        for subnet in layers[layer]:
            sub_list.append('%s' % (subnet))
        cidrs[layer] = '|'.join((cidr) for cidr in sub_list)

    print json.dumps(cidrs)

