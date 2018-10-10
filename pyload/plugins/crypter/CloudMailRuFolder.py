# -*- coding: utf-8 -*-
import base64
import re
import urllib.error
import urllib.parse
import urllib.request

from pyload.plugins.internal.Crypter import Crypter
from pyload.plugins.internal.misc import json


class CloudMailRuFolder(Crypter):
    __name__ = "CloudMailRuFolder"
    __type__ = "crypter"
    __version__ = "0.01"
    __status__ = "testing"

    __pattern__ = r'https?://cloud\.mail\.ru/public/.+'
    __config__ = [
        ("activated",
         "bool",
         "Activated",
         True),
        ("use_premium",
         "bool",
         "Use premium account if available",
         True),
        ("folder_per_package",
         "Default;Yes;No",
         "Create folder for each package",
         "Default"),
        ("max_wait",
         "int",
         "Reconnect if waiting time is greater than minutes",
         10)]

    __description__ = """Cloud.mail.ru decrypter plugin"""
    __license__ = "GPLv3"
    __authors__ = [("GammaC0de", "nitzo2001[AT]yahoo[DOT]com")]

    def decrypt(self, pyfile):
        self.data = self.load(pyfile.url)

        m = re.search(r'window\.cloudSettings\s*=\s*(\{.+?\});', self.data, re.S)
        if m is None:
            self.fail(_("Json pattern not found"))

        json_data = json.loads(m.group(1).replace("\\x3c", "<"))

        pack_links = ["https://cloud.mail.ru/dl?q={}" %
                      base64.b64encode(json.dumps({'u': "{}{}?etag={}&key={}" %
                                                        (json_data['dispatcher']['weblink_view'][0]['url'],
                                                         urllib.parse.quote(_link['weblink']),
                                                         _link['hash'],
                                                         json_data['params']['tokens']['download']),
                                                   'n': urllib.parse.quote_plus(_link['name']),
                                                   's': _link['size']}))
                      for _link in json_data['folders']['folder']['list']
                      if _link['kind'] == "file"]

        if pack_links:
            self.packages.append(
                (pyfile.package().name, pack_links, pyfile.package().folder))
