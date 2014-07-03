#!/usr/bin/python
# vim: set fileencoding=utf-8 :
#
# Somewhat based on
# http://andreas.jakum.net/blog/2012/10/27/new-switch-d-link-dgs-1100-16
#
# Get events from a DGS1100-24
#
# (C) 2014 Guido Günther <agx@sigxcpu.org>
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import socket
import sys
from optparse import OptionParser 

class SmartConsoleMsg(object):
    # 0x00-0x03: unknown (observed: 00 02 00 01) - boot version?
    # 0x04-0x09: switch mac address
    # 0x10-0x2B: unknown
    # 0x2C-0x36: model
    # 0x37     : ' '
    # 0x38     : '('
    # 0x39-0x4C: code
    # 0x3D     : ')'
    # 0x3E     : msg
    def __init__(self, mac, model, code, msg):
        self.mac = mac
        self.model = model
        self.code = code
        self.msg = msg

    @classmethod 
    def from_data(cls, data):
        model = data[0x2C:0x37]
        mac = data[0x04:0x0A]
        msg = data[0x3E:]
        code = data[0x39:0x3D]
        return cls(mac=mac,
                   model=model,
                   code=code,
                   msg=msg)

def mac_to_string(mac):
    return ''.join( [ "%02X-" % ord( x ) for x in mac ] ).strip('-')

def main(argv):
    port = 64514
    parser = OptionParser(usage='%prog [options]')
    parser.add_option("--switch-ip", dest="switchip",
                      default='10.90.90.90',
                      help="IP of the switch to monitor")
    (options, args) = parser.parse_args(argv[1:])
    
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)
    sock.bind(('', port))
    
    while True:
        data, addr = sock.recvfrom(1024)
        if addr[0] == options.switchip:
            msg = SmartConsoleMsg.from_data(data)
            print """Event on %s
    Model: %s
    Code: %s
    Msg: %s
    """ % (mac_to_string(msg.mac), msg.model, msg.code, msg.msg)

if  __name__ == '__main__':
    sys.exit(main(sys.argv))

