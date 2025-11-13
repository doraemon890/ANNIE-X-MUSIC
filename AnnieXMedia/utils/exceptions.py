from typing import Union

class AssistantErr(Exception):
    def __init__(self, errr: str):
        super().__init__(errr)

IGNORED_ERROR_KEYWORDS = [
    "Nᴏ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ғᴏᴜɴᴅ",
    "لم يتم العثور على مكالمة فيديو نشطة",
    "Активный видеочат не найден",
    "Aktif video sohbet bulunamadı",
    "कोई सक्रिय वीडियोचैट नहीं मिला।"
]

IGNORED_EXCEPTION_CLASSES = (
    
)

def is_ignored_error(err: Union[Exception, BaseException]) -> bool:
    if isinstance(err, IGNORED_EXCEPTION_CLASSES):
        return True

    err_str = str(err).lower()
    return any(keyword.lower() in err_str for keyword in IGNORED_ERROR_KEYWORDS)
