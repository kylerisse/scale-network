# Autoflash

## Intro

There has been significant work on the autofashing process for the APs used at SCaLE. As opposed to having to leverage
the [traditional flashing process](./AR71XX.md#flashing).

We now have an autoflashing process that takes place soley inside out CI process and leverages external runners to
physical hardware hosted elsewhere. This document will explain how to configure a raspberry pi and corresponding AP to be
setup for autoflashing.

## Slash command

This is an outline for how to trigger a build on a PR thats in scale-network:

1. Have write access to the repo and push branch directly to the repo. This is needed since we have gitlab mirroring our
   repo.
1. Generate a wormhole string using wormhole and the image to be flashed:

```
~$ wormhole send /openwrt-ath79-generic-netgear_wndr3800ch-squashfs-factory.img
Wormhole code is: 8-amusement-drumbeat
```

3. Take wormhole code `8-amusement-drumbeat` and pass it along to our `tux` slash command as a PR comment:

```
/tux openwrt flash 8-amusement-drumbeat
```

4. This will kickoff the flash and reply with a gitlab pipeline URL.

## Hardware Prereqs

We'll be using the Raspberry Pi 4 for our autoflash coordinator. This should work with any version of the Pi
or similar hardware and the appropriate OS img.

Parts list:

1. Tek Republic TUN-300 - Works well with FreeBSD but any USB interface using the ue driver should work
1. Raspberry Pi - Any model should do just make sure the image being flashed matches the architecture
1. Raspberry Pi Power Adapter - Will need to modify
1. Relay - Currently using [these from Amazon](https://www.amazon.com/gp/product/B07PNB86R7)
1. AP Board - Currently only have this working for WNDR-3700v2 and WNDR-3800[CH]

Wiring:

1. Splice power adapter ground (white dashes) wire and connect to relay points:

```
Wall Wart -> COMM
NC -> Barrel Plug
```

2. Other relay points:

```
GND -> Pi pin 9
IN  -> Pi pin 3
VCC -> Pi pin 2
```

3. Next you'll need to solder 2 wires to the board. One to a ground spot and the other to the reset switch.
   Then connect them to the pi:

```
AP Board ground       -> Pi pin 6
AP Board reset switch -> Pi pin 5
```

4. Pi Serial to AP serial:

```
GND -> Pi pin 14
TX  -> Pi pin 10
RX  -> Pi pin 8
```

> Note: TX/RX are flipped from the AP TX/RX
> No need to VCC since serial chipsets already have power from each board

5. Connect USB ethernet interface to LAN port 1 (closest to the barrel plug) on the AP

References:

- Pi header (pins) diagram: https://www.raspberrypi.org/documentation/usage/gpio/

## Software Prereqs

Using `FreeBSD pi4` image:

```
SHA512 (FreeBSD-13.0-STABLE-arm64-aarch64-RPI-20211230-3684bb89d52-248759.img.xz) = bd3ac2e7a7190afeb4763d7aacc4e5587d675f49c04b5cab59c40220e1d6c16655aa168f26a0531591d946d98343df5eb3b134b71bd5521e93a1bd3d3ac38fa1
```

> Using STABLE since RELEASE was too old and had firmware problems reading for SD card slot
> See: https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=255080
> If using 13.0-RELEASE USB -> SD card adapter did work

`uname -a` on running system resulted in:

```
FreeBSD generic 13.0-STABLE FreeBSD 13.0-STABLE #0 stable/13-n248759-3684bb89d52: Thu Dec 30 03:49:13 UTC 2021     root@releng3.nyi.freebsd.org:/usr/obj/usr/src/arm64.aarch64/sys/GENERIC  arm64
```

Install pkgs:

```
$ pkg update
$ pkg install -y bash expect \
               ruby rubygem-serverspec \
               rubygem-rake curl sudo \
               py38-magic-wormhole git \
               dnsmasq gitlab-runner \
               socat
```

Disable the tty console for pi so that we can use to it monitor the AP

```
$ vim /boot/loader.conf
# Comment out
#boot_multicons="YES"
#boot_serial="YES"
```

Remove configuration for tty:

```
$ vim /etc/ttys
# Comment out
#ttyu0  "/usr/libexec/getty 3wire"      vt100   onifconsole secure
$ kill -HUP 1
```

Register the gitlab-runner (one time operation). [More notes here](https://docs.gitlab.com/runner/register/index.html#freebsd):

```
$ sudo -u gitlab-runner -H /usr/local/bin/gitlab-runner register
```

> Reach out to Rob for registration token for the gitlab-runner

```
$ cat << EOF > /etc/rc.conf
hostname="generic"
#ifconfig_DEFAULT="DHCP"
ifconfig_genet0="DHCP"
sshd_enable="YES"
sendmail_enable="NONE"
sendmail_submit_enable="NO"
sendmail_outbound_enable="NO"
sendmail_msp_queue_enable="NO"
growfs_enable="YES"
gitlab_runner_enable="YES"
ntpdate_enable="YES"
ntpdate_hosts="in.pool.ntp.org"
ifconfig_ue0_name="flash0"
EOF
```

> Set the `flash0` interface to `ue0` but your interface might be different
> Ensure that dhclient isnt defaulting to all interfaces, just genet0

Enable `sudo` elevation without password for gitlab-runner using `visudo` and add:

```
gitlab-runner ALL=(ALL) NOPASSWD: ALL
```

Set `gitlab-runner` users default shell to bash:

```
pw usermod gitlab-runner -s /usr/local/bin/bash
```

> This might just need to be fixed upstream since its set to nologin by default

Thats it! And you should be able to confirm your runner is up and running by looking at
[Gitlab settings](https://gitlab.com/socallinuxexpo/scale-network/-/settings/ci_cd#js-runners-settings)

Additionally considerations:

- Make sure USB interface connected to Pi is set to interface `ue1`
- `serverspec` needs to be passed `LOGIN_PASSWORD` environment var to match default pass for image (current set in gitlab
  CI env var at runtime)
- Double check [hardware prereqs](#hardware-preqs)

## Troubleshooting

1. Checking AP for renewals that are being unanswered:

Startup `tcpdump` on each side:

```
tcpdump -vvv -n -i <IF> udp port 67 or udp port 68
```

2. Uncomment the rsyslog local log on the AP by uncomment confg in `/etc/rsyslog`

## Known issues

1. If you choose to run on the Pi2 (armv6) youll need to manually build the gitlab-runner from source:

- Build gitlab-runner from source and instructions here: https://gitlab.com/gitlab-org/gitlab-runner/-/issues/6694#note_307517264 (go 1.13 required)
- Copy gitlab-runner binary to pi2

2. Pi4 might have issue booting due to text being sent from the serial interface of the AP and boot loader treating it as
   input. Red LED indicator will remain on if this is happening. In these cases power off the AP when rebooting or
   powering on the Pi initially.
