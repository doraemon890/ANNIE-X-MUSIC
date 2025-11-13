from ANNIEMUSIC.core.bot import MusicBotClient
from ANNIEMUSIC.core.dir import StorageManager
from ANNIEMUSIC.core.git import git
from ANNIEMUSIC.core.userbot import Userbot
from ANNIEMUSIC.misc import dbb, heroku

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
