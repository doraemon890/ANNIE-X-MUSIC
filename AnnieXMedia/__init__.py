from AnnieXMedia.core.bot import MusicBotClient
from AnnieXMedia.core.dir import StorageManager
from AnnieXMedia.core.git import git
from AnnieXMedia.core.userbot import Userbot
from AnnieXMedia.misc import dbb, heroku

from .logging import LOGGER

StorageManager()
git()
dbb()
heroku()

app = MusicBotClient()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
