#!/usr/bin/env python3
"""
Tests for inventory.py
"""

import inventory


def test_getfilelineshdr():
    """test cases for getfilelines() with header no building"""
    cases = [
        [
            "testdata/testaps.csv",
            ["n7a-0093,e0:46:9a:5a:c0:36\n", "n8c-0002,2c:b0:5d:7f:63:72\n"],
        ],
        [
            "testdata/testapuse.csv",
            [
                "101-a,n7a-0093,10.128.3.150,6,36,0,0,50,50\n",
                "101-b,n8c-0002,10.128.3.151,1,165,0,0,50,50\n",
            ],
        ],
        [
            "testdata/testpiuse.csv",
            [
                "pi-expo6,pi4-022,110\n",
            ],
        ],
        [
            "testdata/testpis.csv",
            [
                "pi4-022,dc:a6:32:41:88:f4,dea6:32ff:fe41:88f4\n",
            ],
        ],
        ["testdata/testrouterlist.csv", ["br-mdf-01,2001:470:f325:103::2\n"]],
        [
            "testdata/testserverlist.csv",
            [
                "server1,4c:72:b9:7c:41:17,2001:470:f325:503::5,10.128.3.5,core\n",
                "server2,4c:72:b9:7c:40:ec,,,\n",
            ],
        ],
    ]
    for filename, lines in cases:
        assert inventory.getfilelines(filename, header=True) == lines, filename


def test_getfilelinesnobldg():
    """test cases for getfilelines() no header no building"""
    cases = [
        [
            "testdata/testvlans",
            [
                "// Expo Center -- VLANS 100-499\n",
                "#include dir.d/Expo\n",
                "\n",
                "// Conference Center -- VLANS 500-899\n",
                "#include dir.d/Conference\n",
                "\n",
            ],
        ]
    ]
    for filename, lines in cases:
        assert inventory.getfilelines(filename) == lines, filename


def test_getfilelinesbldg():
    # pylint: disable=line-too-long
    """test cases for the getfilelines() no header with building"""
    cases = [
        [
            "Conference",
            [
                "//\tConference\tCenter\t--\tVLANS\t500-899\n",
                "VLAN\tcfSCALE-SLOW	\t500\t2001:470:f325:500::/64\t10.128.128.0/21\t2.4G Wireless Network in Conference Center\n",
                "VLAN\tcfSigns\t\t\t507\t2001:470:f325:507::/64	0.0.0.0/0\tSigns network (Conference Center) IPv6 Only\n",
                "//510-599 not used\n",
            ],
        ],
        [
            "Expo",
            [
                "// Expo Center -- VLANS 100-499\n",
                "VLAN\texSCALE-SLOW\t\t100\t2001:470:f325:100::/64\t10.0.128.0/21\t2.4G Wireless Network in Expo Center\n",
                "//106 not used\n",
                "//112 through 199 not used\n",
                "//200 through 499 Vendors\n",
                "//200-498 are dynamically generated from Booth information file as Vendor VLANs.\n",
                "//The difference is that these VLAN interfaces will also be built with firewall filters to prevent access to other\n",
                "//VLANs (vendor_vlan <-> internet only)\n",
                "VVRNG\tvendor_vlan_\t\t200-201\t2001:470:f325::/48\t10.2.0.0/15\tDynamically allocated and named booth VLANs\n",
                "//499 is reserved for the Vendor backbone VLAN between the Expo switches and the routers.\n",
            ],
        ],
    ]
    for filename, caseslines in cases:
        filelines = inventory.getfilelines(
            filename, directory="./testdata/dir.d/", building="testbuilding"
        )
        for i, line in enumerate(caseslines):
            assert filelines[i] == [line, "testbuilding"], line


def test_dhcp6ranges():
    """test cases for the dhcp6ranges() function"""
    cases = [
        [
            ["2001:470:f325:504::", 64],
            [
                "2001:470:f325:504:d8c::1",
                "2001:470:f325:504:d8c::800",
            ],
        ],
        [
            ["2001:470:f325:111::", 64],
            ["2001:470:f325:111:d8c::1", "2001:470:f325:111:d8c::800"],
        ],
        [["::", 0], ["", ""]],
    ]
    for case, ranges in cases:
        prefix, bitmask = case
        assert inventory.dhcp6ranges(prefix, bitmask) == ranges, (
            prefix + "/" + str(bitmask)
        )


def test_dhcp4ranges():
    """test cases for the dhcp4ranges() function"""
    cases = [
        [
            ["10.0.136.0", 21],
            [
                "10.0.136.80",  # dhcp range start
                "10.0.143.254",  # dhcp range end
                "10.0.136.1",  # default route
            ],
        ],
        [
            ["10.0.2.0", 24],
            [
                "10.0.2.80",  # dhcp range start
                "10.0.2.254",  # dhcp range end
                "10.0.2.1",  # default route
            ],
        ],
        [["0.0.0.0", 0], ["", "", "", "", ""]],
        [["38.98.46.128", 25], ["", "", "", "", ""]],
    ]
    for case, ranges in cases:
        prefix, bitmask = case
        assert inventory.dhcp4ranges(prefix, bitmask) == ranges, (
            prefix + "/" + str(bitmask)
        )


def test_makevlan():
    """test cases for the makevlan() function"""
    cases = [
        [
            "VLAN\tcfCTF\t\t504\t2001:470:f325:504::/64\t10.128.4.0/24\tCapture the Flag",
            {
                "name": "cfCTF",
                "id": "504",
                "ipv6prefix": "2001:470:f325:504::",
                "ipv6bitmask": "64",
                "ipv4prefix": "10.128.4.0",
                "ipv4bitmask": "24",
                "building": "Conference",
                "description": "Capture the Flag",
                "ipv6dhcpStart": "2001:470:f325:504:d8c::1",
                "ipv6dhcpEnd": "2001:470:f325:504:d8c::800",
                "ipv4dhcpStart": "10.128.4.80",
                "ipv4dhcpEnd": "10.128.4.254",
                "ipv4router": "10.128.4.1",
                "ipv4netmask": "255.255.255.0",
                "ipv6dns1": "",
                "ipv6dns2": "",
                "ipv4dns1": "",
                "ipv4dns2": "",
            },
        ],
        ["VLAN\tBadVLAN\t\tABC\t2001:470:f325:504::/64\t10.128.4.0/24\tBad VLAN", None],
    ]
    for line, vlan in cases:
        assert inventory.makevlan(line, "Conference") == vlan, line


def test_bitmasktonetmask():
    """test cases for the bitmasktonetmask() function"""
    cases = [
        [16, None],
        [17, "255.255.128.0"],
        [18, "255.255.192.0"],
        [19, "255.255.224.0"],
        [20, "255.255.240.0"],
        [21, "255.255.248.0"],
        [22, "255.255.252.0"],
        [23, "255.255.254.0"],
        [24, "255.255.255.0"],
        [25, None],
    ]
    for bitmask, netmask in cases:
        assert inventory.bitmasktonetmask(bitmask) == netmask, bitmask


def test_genvlans():
    """test cases for the genvlans() function"""
    cases = [
        [
            "VVRNG\ttest_vlan_\t\t200-201\t2001:470:f325::/48\t10.2.0.0/15\tdynamic vlan",
            [
                {
                    "name": "test_vlan_200",
                    "id": 200,
                    "ipv6prefix": "2001:470:f325:200::",
                    "ipv6bitmask": 64,
                    "ipv4prefix": "10.2.0.0",
                    "ipv4bitmask": 24,
                    "building": "Expo",
                    "description": "Dyanmic vlan 200",
                    "ipv6dhcpStart": "2001:470:f325:200:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:200:d8c::800",
                    "ipv4dhcpStart": "10.2.0.80",
                    "ipv4dhcpEnd": "10.2.0.254",
                    "ipv4router": "10.2.0.1",
                    "ipv4netmask": "255.255.255.0",
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
                {
                    "name": "test_vlan_201",
                    "id": 201,
                    "ipv6prefix": "2001:470:f325:201::",
                    "ipv6bitmask": 64,
                    "ipv4prefix": "10.2.1.0",
                    "ipv4bitmask": 24,
                    "building": "Expo",
                    "description": "Dyanmic vlan 201",
                    "ipv6dhcpStart": "2001:470:f325:201:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:201:d8c::800",
                    "ipv4dhcpStart": "10.2.1.80",
                    "ipv4dhcpEnd": "10.2.1.254",
                    "ipv4router": "10.2.1.1",
                    "ipv4netmask": "255.255.255.0",
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
            ],
        ]
    ]
    for line, vlans in cases:
        assert inventory.genvlans(line, "Expo") == vlans, line


def test_ip4toptr():
    """test cases for the ip4toptr() function"""
    cases = [
        ["10.128.3.5", "5.3.128.10.in-addr.arpa"],
        ["10.0.3.200", "200.3.0.10.in-addr.arpa"],
    ]
    for ipaddr, ptr in cases:
        assert inventory.ip4toptr(ipaddr) == ptr, ipaddr


def test_ip6toptr():
    """test cases for the ip6toptr() function"""
    cases = [
        [
            "2001:470:f325:103::200:4",
            "4.0.0.0.0.0.2.0.0.0.0.0.0.0.0.0.3.0.1.0.5.2.3.f.0.7.4.0.1.0.0.2.ip6.arpa",
        ],
        [
            "2001:470:f325:107:ad84:2d06:1dfe:7f67",
            "7.6.f.7.e.f.d.1.6.0.d.2.4.8.d.a.7.0.1.0.5.2.3.f.0.7.4.0.1.0.0.2.ip6.arpa",
        ],
    ]
    for ipaddr, ptr in cases:
        assert inventory.ip6toptr(ipaddr) == ptr, ipaddr


def test_isvalidip():
    """test cases for the isvalidip() function"""
    cases = [
        ["127.0.0.1", True],
        ["::1", True],
        ["10.1.1.1", True],
        ["2001:470:f325:107:8bfa:646e:811:241c", True],
        ["string", False],
        ["FFFF:VT40:f325:107:8bfa:646e:811:241c", False],
        ["256.0.0.1", False],
        ["2001:470:f325:107:8bfa:646e:811", False],
    ]
    for ipaddr, result in cases:
        assert inventory.isvalidip(ipaddr) == result, ipaddr


def test_roomalias():
    """test cases for the roomalias() function"""
    cases = [["Rm101-102", ["rm101", "rm102"]], ["BallroomC", []]]
    for name, aliases in cases:
        assert inventory.roomalias(name) == aliases, name


def test_populatevlans():
    # pylint: disable=line-too-long
    """test cases for the populatevlans() function"""
    cases = [
        [
            ["./testdata/", "testvlans"],
            [
                {
                    "name": "exSCALE-SLOW",
                    "id": "100",
                    "ipv6prefix": "2001:470:f325:100::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "10.0.128.0",
                    "ipv4bitmask": "21",
                    "building": "Expo",
                    "description": "2.4G Wireless Network in Expo Center",
                    "ipv6dhcpStart": "2001:470:f325:100:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:100:d8c::800",
                    "ipv4dhcpStart": "10.0.128.80",
                    "ipv4dhcpEnd": "10.0.135.254",
                    "ipv4router": "10.0.128.1",
                    "ipv4netmask": "255.255.248.0",
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
                {
                    "name": "vendor_vlan_200",
                    "id": 200,
                    "ipv6prefix": "2001:470:f325:200::",
                    "ipv6bitmask": 64,
                    "ipv4prefix": "10.2.0.0",
                    "ipv4bitmask": 24,
                    "building": "Expo",
                    "description": "Dyanmic vlan 200",
                    "ipv6dhcpStart": "2001:470:f325:200:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:200:d8c::800",
                    "ipv4dhcpStart": "10.2.0.80",
                    "ipv4dhcpEnd": "10.2.0.254",
                    "ipv4router": "10.2.0.1",
                    "ipv4netmask": "255.255.255.0",
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
                {
                    "name": "vendor_vlan_201",
                    "id": 201,
                    "ipv6prefix": "2001:470:f325:201::",
                    "ipv6bitmask": 64,
                    "ipv4prefix": "10.2.1.0",
                    "ipv4bitmask": 24,
                    "building": "Expo",
                    "description": "Dyanmic vlan 201",
                    "ipv6dhcpStart": "2001:470:f325:201:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:201:d8c::800",
                    "ipv4dhcpStart": "10.2.1.80",
                    "ipv4dhcpEnd": "10.2.1.254",
                    "ipv4router": "10.2.1.1",
                    "ipv4netmask": "255.255.255.0",
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
                {
                    "name": "cfSCALE-SLOW",
                    "id": "500",
                    "ipv6prefix": "2001:470:f325:500::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "10.128.128.0",
                    "ipv4bitmask": "21",
                    "building": "Conference",
                    "description": "2.4G Wireless Network in Conference Center",
                    "ipv6dhcpStart": "2001:470:f325:500:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:500:d8c::800",
                    "ipv4dhcpStart": "10.128.128.80",
                    "ipv4dhcpEnd": "10.128.135.254",
                    "ipv4router": "10.128.128.1",
                    "ipv4netmask": "255.255.248.0",
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
                {
                    "name": "cfSigns",
                    "id": "507",
                    "ipv6prefix": "2001:470:f325:507::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "0.0.0.0",
                    "ipv4bitmask": "0",
                    "building": "Conference",
                    "description": "Signs network (Conference Center) IPv6 Only",
                    "ipv6dhcpStart": "2001:470:f325:507:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:507:d8c::800",
                    "ipv4dhcpStart": "",
                    "ipv4dhcpEnd": "",
                    "ipv4router": "",
                    "ipv4netmask": None,
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
            ],
        ]
    ]
    for case, vlans in cases:
        swconfigdir, vlansfile = case
        assert inventory.populatevlans(swconfigdir, vlansfile) == vlans, case


def test_populateswitches():
    """test cases for the populateswitches() function"""
    cases = [
        [
            "./testdata/testswitchtypes",
            [
                {
                    "name": "expo-catwalk",
                    "fqdn": "expo-catwalk.scale.lan",
                    "num": "16",
                    "ipv6": "2001:470:f325:103::200:16",
                    # pylint: disable=line-too-long
                    "ipv6ptr": "6.1.0.0.0.0.2.0.0.0.0.0.0.0.0.0.3.0.1.0.5.2.3.f.0.7.4.0.1.0.0.2.ip6.arpa",
                    "aliases": [],
                },
                {
                    "name": "rm209-210",
                    "fqdn": "rm209-210.scale.lan",
                    "num": "17",
                    "ipv6": "2001:470:f325:503::200:17",
                    # pylint: disable=line-too-long
                    "ipv6ptr": "7.1.0.0.0.0.2.0.0.0.0.0.0.0.0.0.3.0.5.0.5.2.3.f.0.7.4.0.1.0.0.2.ip6.arpa",
                    "aliases": ["rm209", "rm210"],
                },
            ],
        ]
    ]
    for filename, switches in cases:
        assert inventory.populateswitches(filename) == switches, filename


def test_populaterouters():
    """test cases for the populaterouters() function"""
    cases = [
        [
            "./testdata/testrouterlist.csv",
            [
                {
                    "name": "br-mdf-01",
                    "fqdn": "br-mdf-01.scale.lan",
                    "ipv6": "2001:470:f325:103::2",
                    # pylint: disable=line-too-long
                    "ipv6ptr": "2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.3.0.1.0.5.2.3.f.0.7.4.0.1.0.0.2.ip6.arpa",
                }
            ],
        ]
    ]
    for filename, routers in cases:
        assert inventory.populaterouters(filename) == routers, filename


def test_populateaps():
    """test cases for the populateaps() function"""
    cases = [
        [
            "./testdata/testaps.csv",
            "./testdata/testapuse.csv",
            [
                {
                    "name": "101-a",
                    "fqdn": "101-a.scale.lan",
                    "mac": "e0:46:9a:5a:c0:36",
                    "ipv4": "10.128.3.150",
                    "ipv4ptr": "150.3.128.10.in-addr.arpa",
                    "wifi2": "6",
                    "wifi5": "36",
                    "configver": "0",
                    "aliases": ["n7a-0093"],
                },
                {
                    "name": "101-b",
                    "fqdn": "101-b.scale.lan",
                    "mac": "2c:b0:5d:7f:63:72",
                    "ipv4": "10.128.3.151",
                    "ipv4ptr": "151.3.128.10.in-addr.arpa",
                    "wifi2": "1",
                    "wifi5": "165",
                    "configver": "0",
                    "aliases": ["n8c-0002"],
                },
            ],
        ]
    ]
    for aps, apuse, apsmerged in cases:
        assert inventory.populateaps(aps, apuse) == apsmerged


def test_populatepis():
    """test cases for the populatepis() function"""
    cases = [
        [
            "./testdata/testpis.csv",
            "./testdata/testpiuse.csv",
            [
                {
                    "name": "pi-expo6",
                    "fqdn": "pi-expo6.scale.lan",
                    "ipv6": "2001:470:f026:110:dea6:32ff:fe41:88f4",
                    # pylint: disable=line-too-long
                    "ipv6ptr": "4.f.8.8.1.4.e.f.f.f.2.3.6.a.e.d.0.1.1.0.6.2.0.f.0.7.4.0.1.0.0.2.ip6.arpa",
                }
            ],
        ]
    ]
    for pisfilename, piusefilename, pis in cases:
        assert inventory.populatepis(pisfilename, piusefilename) == pis, (
            f"{pisfilename} {piusefilename}"
        )


def test_populateservers():
    """test cases for the populateservers() function"""
    mocvlans = [
        {
            "name": "cfInfra",
            "ipv6prefix": "2001:470:f325:503::",
            "building": "Conference",
        }
    ]
    cases = [
        [
            "./testdata/testserverlist.csv",
            [
                {
                    "aliases": [],
                    "fqdn": "server1.scale.lan",
                    "ipv4ptr": "5.3.128.10.in-addr.arpa",
                    # pylint: disable=line-too-long
                    "ipv6ptr": "5.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.3.0.5.0.5.2.3.f.0.7.4.0.1.0.0.2.ip6.arpa",
                    "name": "server1",
                    "macaddress": "4c:72:b9:7c:41:17",
                    "ipv6": "2001:470:f325:503::5",
                    "ipv4": "10.128.3.5",
                    "role": "core",
                    "vlan": "cfInfra",
                    "building": "Conference",
                }
            ],
        ]
    ]
    for filename, servers in cases:
        assert inventory.populateservers(filename, mocvlans) == servers, filename
