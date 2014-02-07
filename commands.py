# -*- coding: ISO-8859-1 -*-
import timeside
import json
import re
import urllib
import os


class CommandParser:
    irc = None
    whois_query = []
    whowas_query = []

    def __init__(self, irc):
        self.irc = irc

    def parseMessage(self, command, sender, channel, carg, args):
        cmd = {
            #'raw':     self.cmd_raw,
            'help':    self.cmd_help,
            'moo':     self.cmd_moo,
            'google':  self.cmd_google,
            'image':   self.cmd_image,
            'spectro': self.cmd_spectro,
            'whois':   self.cmd_whois,
            'whowas':  self.cmd_whowas
        }.get(command, False)

        if not cmd:
            return False

        cmd(sender, channel, carg, args)
        return True

    def cmd_help(self, sender, channel, carg, args):
        '''Lists publically available commands'''

        self.irc.PRIVMSG(sender, u'!hitsu.moo       hitsujiBOT will moo at you')
        self.irc.PRIVMSG(sender, u'!hitsu.image     hitsujiBOT displays a link to the current steganogram')
        self.irc.PRIVMSG(sender, u'!hitsu.spectro   hitsujiBOT displays a link to a spectrogram of a given youtube video')
        self.irc.PRIVMSG(sender, u'!hitsu.whois     hitsujiBOT displays a link to a whois lookup')
        self.irc.PRIVMSG(sender, u'!hitsu.whowas    hitsujiBOT displays a link to a whois lookup for a user that has recently been online')

    def cmd_moo(self, sender, channel, carg, args):
        '''Test command'''
        self.irc.PRIVMSG(sender, u'moo')

    def cmd_google(self, sender, channel, carg, args):
        '''Sarcastic bot command to generate a goole search string. I don't
        know why, but people are actually using this a lot'''
        if not carg:
            self.irc.PRIVMSG(channel, u'!hitsu.google <search query>')
        else:
            self.irc.PRIVMSG(channel, u'http://lmgtfy.com/?q={0}'
                .format(urllib.quote_plus(carg)))

    def cmd_raw(self, sender, channel, carg, args):
        '''Used to allow an admin out send RAW messages. Potentially dangerous
        command so should only be enabled when necessary'''
        self.irc.send(carg)

    def cmd_image(self, sender, channel, carg, args):
        '''Returns a link to the generated image from the YouTube videos'''

        self.irc.PRIVMSG(channel,
                         'http://77days.tenmilesout.net/images/output1-lrg.png'
                         )
        self.irc.PRIVMSG(channel,
                         'http://77days.tenmilesout.net/images/output2-lrg.png'
                         )

    def cmd_whois(self, sender, channel, carg, args):
        '''Looks up a users whois info to get their hostname and from that
        generates a url to allow a channel OP identify a user'''

        target = args[3].split(None, 1)

        if len(target) == 1:
            self.irc.PRIVMSG(channel,
                             '!{0}.whois <user>'.format(self.irc.trigger))

        target = target[1].strip()

        name = carg.split(None, 1)[0]

        query = {'name': name, 'channel': channel, 'handled': False}
        self.whois_query.append(query)
        self.irc.WHOIS(name)

    def response_whois(self, args):
        '''callback to process a users whois info'''

        if args[1] == '311':
            parts = args[3].split(None, 3)
            name = parts[0]
            address = parts[2]

            for i in self.whois_query:
                if i['name'].lower() == name.lower() and not i['handled']:
                    i['handled'] = True

                    if address.startswith('service'):
                        self.irc.PRIVMSG(i['channel'],
                                         i['name'] + ' is a service')

                    elif address.startswith('unaffiliated'):
                        self.irc.PRIVMSG(i['channel'],
                                         i['name'] + ' is cloaked')

                    elif address.startswith('gateway/web/freenode/ip.'):
                        self.irc.PRIVMSG(i['channel'],
                            'http://houston.dnstools.com/?count=1&target={0}'
                                .format(address[24:]))
                    else:
                        self.irc.PRIVMSG(i['channel'],
                            'http://houston.dnstools.com/?count=1&target={0}'
                                .format(address))

        elif args[1] == '318':
            name = args[3].split(None, 1)[0]

            for i in self.whois_query:
                if i['name'].lower() == name.lower():

                    if not i['handled']:
                        self.irc.PRIVMSG(i['channel'],
                                         '{0}{1}'.format(i['name'],
                                                         ': no such nick'))

                    self.whois_query.pop(self.whois_query.index(i))
                    break

    def cmd_whowas(self, sender, channel, carg, args):
        '''Looks up a users whowas info to get their hostname and from that
        generates a url to allow a channel OP identify a user'''
        name = carg.split(None, 1)[0]

        query = {'name': name, 'channel': channel, 'handled': False}
        self.whowas_query.append(query)

        self.irc.WHOWAS(name)

    def response_whowas(self, args):
        '''callback to process a users whowas info'''

        if args[1] == '314':
            parts = args[3].split(None, 3)
            name = parts[0]
            address = parts[2]

            for i in self.whowas_query:

                if i['name'].lower() == name.lower() and not i['handled']:
                    i['handled'] = True

                    if address.startswith('service'):
                        self.irc.PRIVMSG(i['channel'], '{0}{1}'.format(
                            i['name'],
                            ' is a service'))

                    elif address.startswith('unaffiliated'):
                        self.irc.PRIVMSG(i['channel'], '{0}{1}'.format(
                            i['name'],
                            ' is cloaked'))
                    elif address.startswith('gateway/web/freenode/ip.'):
                        self.irc.PRIVMSG(i['channel'],
                            'http://houston.dnstools.com/?count=1&target={0}'.format(address[24:]))
                    else:
                        self.irc.PRIVMSG(i['channel'],
                            'http://houston.dnstools.com/?count=1&target={0}'.format(address))

        elif args[1] == '369':
            name = args[3].split(None, 1)[0]
            for i in self.whowas_query:
                if i['name'].lower() == name.lower():
                    if not i['handled']:
                        self.irc.PRIVMSG(i['channel'], '{0}{1}'.format(
                            i['name'], ': no such nick'))
                    self.whowas_query.pop(self.whowas_query.index(i))
                    break

    def cmd_spectro(self, sender, channel, carg, args):
        '''create a spectrogram of a youtube video'''

        allowed_channels = [
            'pronunciationbook',
            'videoroyale']
        img_dir = os.path.realpath(os.path.dirname(__file__) + '/data/img')
        mp4_dir = os.path.realpath(os.path.dirname(__file__) + '/data/mp4')
        wav_dir = os.path.realpath(os.path.dirname(__file__) + '/data/wav')

        args = args[3].split(None, 1)
        if len(args) == 1:
            self.irc.PRIVMSG(channel,
                '!{0}.spectro <youtube video url>'.format(self.irc.trigger))
            return

        id, author = self.get_youtube_id(args[1])

        if not id:
            self.irc.PRIVMSG(channel, 'invalid youtube url')
            return

        if author.lower() not in allowed_channels:
            clist = ', '.join(allowed_channels))
            self.irc.PRIVMSG(channel,
                'can only process videos from channels: {0}'.format(clist)
            return

        url = 'http://77days.tenmilesout.net/spectros/{0}.png'.format(id)

        if not os.path.exists('{0}/{1}.png'.format(img_dir, id):
            # This takes a while, so let the user know its doing something
            self.irc.PRIVMSG(sender, 'video confirmed, processing now')

            cmd = 'cd {0}; youtube-dl http://www.youtube.com/watch?v={1}' \
                .format(mp4_dir, id)
            os.popen(cmd, 'r').read()

            file = None
            for f in os.listdir(mp4_dir):
                if f.endswith(id + '.mp4') or f.endswith(id + '.flv'):
                    file = f
                    break

            if not file:
                self.irc.PRIVMSG(sender, 'file downloaded in unknown format')
                return

            self.irc.PRIVMSG(sender, file)

            cmd = 'ffmpeg -y -i "{0}/{1}" "{2}/{3}"' \
                .format(mp4_dir, file, wav_dir, id + '.wav')
            os.popen(cmd, 'r').read()

            # still taking a while. update the user
            self.irc.PRIVMSG(sender, 'generating image')

            decoder = timeside.decoder.FileDecoder(
                '{0}/{1}'.format(wav_dir, id + '.wav'))
            grapher = timeside.grapher.Spectrogram(width=3840, height=256)
            (decoder | grapher).run()
            grapher.render('{0}/{1}'.format(img_dir, id + '.bmp'))

            cmd = 'convert "{0}/{1}" "{0}/{2}"'.format(
                img_dir,
                id + '.bmp',
                id + '.png')
            os.popen(cmd, 'r').read()

        self.irc.PRIVMSG(channel, url)

    def get_youtube_id(self, url):
        '''Get the id of a youtube video from the url'''
        id = None

        ytr = r'^https?://(www\.)?youtube.com/watch\?(.*?&)?v=(.*?)(&.*?)?$'

        match = re.search( ytr, url)
        if match:
            id = match.group(3)
        else:
            match = re.search(r'^https?://youtu.be/(.*?)$', url)
            if not match: return None, None
            id = match.group(1)

        id = id.strip()

        url = 'http://gdata.youtube.com/feeds/api/videos/' + id + '?alt=json'

        handle = urllib.urlopen(url)
        if handle.getcode() != 200:
            return None, None

        author = json.loads(handle.read().decode('ISO-8859-1')) \
            ['entry']['author'][0]['name']['$t']

        return id, author


