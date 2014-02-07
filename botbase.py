#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

import socket


class IRCClient:
    def __init__(self):
        self.connected = False
        self.nickname = None
        self.server = None
        self.port = None
        self.quit = False

        self.socket = socket.socket()
        self.socket.connect((self.server, 6667))
        self.NICK(self.nickname)
        self.USER(self.nickname)

    def log(sef, string):
        try:
            print string
        except:
            print string.encode('ascii', 'ignore')

    def error(self, string):
        self.log(u'\033[91m{0}\033[0m'.format(string))

    def listen(self):
        lines = ['']
        while not self.quit:
            # process 4 KB at a time
            buf = lines[-1] + self.socket.recv(4096).decode('ISO-8859-1')
            lines = buf.split('\r\n')

            for line in lines[:-1]:
                self.processLine(line)

    def processLine(self, line):
        args = line.split(None, 3)

        # no line should contain 0 aruments. If this is enacted then something
        # major went wrong
        if len(args) == 1:  # line not processed
            self.log(u'\033[92m>>\033[91m{0}\033[0m'.format(line))
            return

        # Ping is currently the only command that uses 1 argument
        cmd = {
            'PING': self.recv_PING
        }.get(args[0], False)

        if cmd:
            cmd(args)
            return

        if len(args) == 2:  # line not processed
            self.log(u'\033[92m>>\033[91m{0}\033[0m'.format(line))
            return

        cmd = {
            'JOIN': self.recv_JOIN
        }.get(args[1], False)

        if cmd:
            cmd(args)
            return

        if len(args) == 3:  # line not processed
            self.log(u'\033[92m>>\033[91m{0}\033[0m'.format(line))
            return

        cmd = {
            'MODE':    self.ignore_and_log,
            'NOTICE':  self.ignore_and_log,
            'PRIVMSG': self.recv_PRIVMSG,
            '001': self.ignore_and_log,
            '002': self.ignore_and_log,  # get_host
            '003': self.ignore_and_log,
            '004': self.ignore_and_log,  # modes
            '005': self.ignore_and_log,  # settings
            '250': self.ignore_and_log,
            '251': self.ignore_and_log,
            '252': self.ignore_and_log,
            '253': self.ignore_and_log,
            '254': self.ignore_and_log,
            '255': self.ignore_and_log,
            '265': self.ignore_and_log,
            '266': self.ignore_and_log,
            '311': self.recv_WHOIS,      # WHOIS user
            '312': self.recv_WHOIS,      # WHOIS server
            '313': self.recv_WHOIS,      # WHOIS is op
            '314': self.recv_WHOWAS,     # WHOWAS user
            '317': self.recv_WHOIS,      # WHOIS idle
            '318': self.recv_WHOIS,      # WHOIS END
            '319': self.recv_WHOIS,      # WHOIS channel list
            '353': self.ignore_and_log,  # reply to NAMES
            '366': self.ignore_and_log,  # end of reply to NAMES
            '369': self.recv_WHOWAS,     # WHOWAS END
            '372': self.ignore_and_log,
            '375': self.ignore_and_log,
            '376': self.ignore_and_log,
        }.get(args[1], False)

        if cmd:
            cmd(args)
            return

        # line not processed
        self.log(u'\033[92m>>\033[91m{0}\033[0m'.format(line))

    def send(self, msg, display=True):
        msg = msg.replace('\r', '').replace('\n', '')
        msg = msg[:436] + '..' if len(msg) > 438 else msg
        if display:
            self.log(u'\033[93m<<\033[0m{0}'.format(msg))
        self.socket.send(msg + u"\r\n")

    def recv_JOIN(self, args):
        self.log(u'\033[92m{0}\033[0m'.format(args[2]))

    def recv_PING(self, args):
        self.log(u'\033[92m{0}\033[0m'.format('[PING PONG]'))
        target = args[1][1:]
        self.PONG(target)

    def recv_PRIVMSG(self, args):
        channel = args[2]
        user = args[0].split('!', 1)[0][1:]
        msg = args[3][1:]

        self.log(u'\033[93m{0} \033[92m<{1}> \033[0m{2}'
            .format(channel, user, msg))

    def recv_WHOIS(self, args):
        self.log(u'\033[92m{0} \033[93m{1} \033[0m'.format('WHOIS', args[3]))

    def recv_WHOWAS(self, args):
        self.log(u'\033[92m{0} \033[93m{1} \033[0m'.format('WHOWAS', args[3]))

    def JOIN(self, channel):
        self.send(u"JOIN {0}".format(channel))

    def NICK(self, name):
        self.send(u"NICK {0}".format(name))

    def PONG(self, msg):
        self.send(u"PONG :{0}".format(msg), False)

    def PRIVMSG(self, to, msg, display=True):
        self.send(u"PRIVMSG {0} :{1}".format(to, msg), display)

    def QUIT(self, msg="Quitting"):
        self.send(u"QUIT :{0}".format(msg))

    def USER(self, name):
        self.send(u"USER {0} {0} {0} {0}".format(name))

    def WHOIS(self, name):
        self.send(u"WHOIS {0}".format(name))

    def WHOWAS(self, name):
        self.send(u'WHOWAS {0}'.format(name))

    def ignore(self, *args):
        pass

    def ignore_and_log(self, *args):
        self.log(u'\033[92m>>\033[0m{0}'.format(' '.join(args[0])))
