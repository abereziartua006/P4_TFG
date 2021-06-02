#!/usr/bin/python

#  Copyright 2019-present Open Networking Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import argparse

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import Host
from mininet.topo import Topo
from stratum import StratumBmv2Switch

CPU_PORT = 255


class IPv6Host(Host):
    """Host that can be configured with an IPv6 gateway (default route).
    """

    def config(self, ipv6, ipv6_gw=None, **params):
        super(IPv6Host, self).config(**params)
        self.cmd('ip -4 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -6 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -6 addr add %s dev %s' % (ipv6, self.defaultIntf()))
        if ipv6_gw:
            self.cmd('ip -6 route add default via %s' % ipv6_gw)
        # Disable offload
        for attr in ["rx", "tx", "sg"]:
            cmd = "/sbin/ethtool --offload %s %s off" % (self.defaultIntf(), attr)
            self.cmd(cmd)

        def updateIP():
            return ipv6.split('/')[0]

        self.defaultIntf().updateIP = updateIP

    def terminate(self):
        super(IPv6Host, self).terminate()


class TutorialTopo(Topo):
    """2x2 fabric topology with IPv6 hosts"""

    def __init__(self, *args, **kwargs):
        Topo.__init__(self, *args, **kwargs)

	# Switches
        s1 = self.addSwitch('s1', cls=StratumBmv2Switch, cpuport=CPU_PORT)
	s2 = self.addSwitch('s2', cls=StratumBmv2Switch, cpuport=CPU_PORT)
	#s3 = self.addSwitch('s3', cls=StratumBmv2Switch, cpuport=CPU_PORT)
	#s4 = self.addSwitch('s4', cls=StratumBmv2Switch, cpuport=CPU_PORT)
	#s5 = self.addSwitch('s5', cls=StratumBmv2Switch, cpuport=CPU_PORT)
	#s6 = self.addSwitch('s6', cls=StratumBmv2Switch, cpuport=CPU_PORT)

        # Switch Links
        self.addLink(s1, s2)
        #self.addLink(s1, s4)
	#self.addLink(s1, s5)

	#self.addLink(s2, s3)
	#self.addLink(s3, s4)
	#self.addLink(s3, s6)


	#self.addLink(s4, s5)

	#self.addLink(s5, s6)


        # IPv6 hosts attached to leaf 1
        ha = self.addHost('ha', cls=IPv6Host, mac="00:00:00:00:00:1A",
                           ipv6='2001:1:1::a/64', ipv6_gw='2001:1:1::ff')
        hb = self.addHost('hb', cls=IPv6Host, mac="00:00:00:00:00:1B",
                           ipv6='2001:1:1::b/64', ipv6_gw='2001:1:1::ff')
        #probarako hosta
         hc = self.addHost('hc', cls=IPv6Host, mac="00:00:00:00:00:1C",
                          ipv6='2001:1:1::c/64', ipv6_gw='2001:1:1::ff')
        
        self.addLink(ha, s1)  
        self.addLink(hb, s2)
        #probarako hosta
        self.addLink(hc,s5)


        


def main():
    net = Mininet(topo=TutorialTopo(), controller=None)
    net.start()

    hb = net.get("hb")
    hb.cmd ('/usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf -d')

    CLI(net)
    net.stop()
    print '#' * 80
    print 'ATTENTION: Mininet was stopped! Perhaps accidentally?'
    print 'No worries, it will restart automatically in a few seconds...'
    print 'To access again the Mininet CLI, use `make mn-cli`'
    print 'To detach from the CLI (without stopping), press Ctrl-D'
    print 'To permanently quit Mininet, use `make stop`'
    print '#' * 80


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Mininet topology script for 2x2 fabric with stratum_bmv2 and IPv6 hosts')
    args = parser.parse_args()
    setLogLevel('info')

    main()
