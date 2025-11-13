import os
import asyncio
from PIL import Image
from pyrogram import raw
from pyrogram.file_id import FileId

STICKER_DIMENSIONS = (512, 512)


async def resize_file_to_sticker_size(file_path: str) -> str:
    """
    Resize the image at file_path so its max dimension is 512px and save as PNG.
    Runs the CPU‑bound work in a thread to avoid blocking the event loop.
    """
    def _sync_resize() -> str:
        im = Image.open(file_path).convert("RGBA")
        im.thumbnail(STICKER_DIMENSIONS)
        new_path = file_path if file_path.lower().endswith(".png") else f"{file_path}.png"
        im.save(new_path, "PNG")
        if new_path != file_path:
            os.remove(file_path)
        return new_path

    return await asyncio.to_thread(_sync_resize)


async def upload_document(client, file_path: str, chat_id: int) -> raw.types.InputDocument:
    """
    Upload a file to Telegram and return an InputDocument for raw calls.
    """
    media = await client.invoke(
        raw.functions.messages.UploadMedia(
            peer=await client.resolve_peer(chat_id),
            media=raw.types.InputMediaUploadedDocument(
                file=await client.save_file(file_path),
                mime_type=client.guess_mime_type(file_path) or "application/octet-stream",
                attributes=[
                    raw.types.DocumentAttributeFilename(
                        file_name=os.path.basename(file_path)
                    )
                ],
            ),
        )
    )
    doc = media.document
    return raw.types.InputDocument(
        id=doc.id,
        access_hash=doc.access_hash,
        file_reference=doc.file_reference,
    )


async def get_document_from_file_id(file_id: str) -> raw.types.InputDocument:
    """
    Decode a file_id string into an InputDocument for raw calls.
    """
    decoded = FileId.decode(file_id)
    return raw.types.InputDocument(
        id=decoded.media_id,
        access_hash=decoded.access_hash,
        file_reference=decoded.file_reference,
    )
