# -*- coding: ISO-8859-1 -*-
from botbase import IRCClient
import sys
import time
import re
import json

try:
    import commands
except:
    print '\033[91m{0}\033[0m'.format('CommandParser failed to load')


class MooBot(IRCClient):
    def __init__(self):
        self.admins = []
        self.channels = []
        self.nickserv_pass = None
        self.trigger = None
        self.parser = None

        settings = json.loads(open('settings.json', 'r').read())

        self.server        = settings.get('server',        None    )
        self.port          = settings.get('port',          6667    )
        self.channels      = settings.get('channels',      [ ]     )
        self.nickname      = settings.get('nickname',      'MooBot')
        self.nickserv_pass = settings.get('nickserv_pass', None    )
        self.trigger       = settings.get('trigger',       'moobot').lower()
        self.admins        = settings.get('admins',        [ ]     )

        try:
            self.parser = commands.CommandParser(self)
        except:
            self.error('CommandParser failed to load')

        IRCClient.__init__(self)

        if self.nickserv_pass: self.PRIVMSG('NickServ', 'identify ' + self.nickserv_pass)

        for c in self.channels:
            self.JOIN(c)


    def recv_PRIVMSG(self, args):
        IRCClient.recv_PRIVMSG(self, args)

        command = args[3][1:].split(None, 1)
        carg = command[1].strip() if len(command) == 2 else ''
        try:
            command = command[0].lower()
        except:
            command = ''

        regex = r'^!({0}\.)?(.*?)$'.format(self.trigger)
        match = re.search(regex, command)

        if not match: return

        command = match.group(2)


        sender  = args[0][1:].split('!', 1)[0]
        channel = args[2] if args[2] != self.nickname else sender

        # admin commands

        if sender in self.admins:
            cmd = {
                'quit':   self.cmd_quit,
                'reload': self.cmd_reload
            }.get(command, False)

            if cmd:
                cmd(sender, channel, carg, args)
                return

        # dynamically loaded commands

        if self.parser:
            try:
                if self.parser.parseMessage(command, sender, channel, carg, args): return
            except:
                self.error('Exception raised when processing command: ' + args[3][1:])
                self.PRIVMSG(sender, 'Exception raised when processing command: {0} | {1}'.format(sys.exc_info()[0], sys.exc_info()[1]))
                return


    def recv_WHOIS(self, args):
        if self.parser:
            try:
                self.parser.response_whois(args)
            except:
                self.error('Exception raised when processing whois response')

        IRCClient.recv_WHOIS(self, args)

    def recv_WHOWAS(self, args):
        if self.parser:
            try:
                self.parser.response_whowas(args)
            except:
                self.error('Exception raised when processing whowas response')

        IRCClient.recv_WHOWAS(self, args)


    def cmd_quit(self, sender, channel, carg, args):
        self.log(u'\033[92m{0}\033[0m'.format('[Quitting]'))
        self.QUIT()
        time.sleep(1)
        self.quit = True

    def cmd_reload(self, sender, channel, carg, args):
        self.log(u'\033[92m{0}\033[0m'.format('[Reloading]'))
        self.parser = None

        code = open('commands.py', 'rU').read()

        # will it compile

        try:
            compile(code, 'commands', 'exec')
        except:
            self.error('Error reloading parser: Error in compilation')
            self.PRIVMSG(sender, 'Error in compilation')
            return

        # will it execute

        try:
            execfile('commands.py')
        except:
            self.error('Error reloading parser: Error in execution')
            self.PRIVMSG(sender, 'Error in execution')
            return

        # fuck it... it must be ok... reload the motherfucker

        try:
            reload(sys.modules['commands'])
            self.parser = commands.CommandParser(self)
            self.PRIVMSG(sender, 'Reload complete')
        except:
            self.parser = None
            self.error('Error reloading parser: Error while initing')
            self.PRIVMSG(sender, 'Error while initing')



MooBot().listen()
