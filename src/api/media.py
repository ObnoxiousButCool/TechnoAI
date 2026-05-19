"""Admin media upload endpoint — stores images in the shared media folder."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.security.api_key import APIKeyHeader

from src.config.settings import get_settings

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

_admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


def _require_admin(x_admin_key: str | None = Depends(_admin_key_header)) -> None:
    settings = get_settings()
    if not x_admin_key or x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Forbidden")


# ── Allowed image types ───────────────────────────────────────────────────────

_ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".jpg", ".jpeg", ".png", ".webp", ".gif"})

# Magic byte signatures used to validate actual file content.
# Order matters: longer/more-specific signatures should come first.
_IMAGE_SIGNATURES: list[tuple[bytes, str]] = [
    (b"\x89PNG\r\n\x1a\n", "image/png"),  # PNG
    (b"\xff\xd8\xff",       "image/jpeg"), # JPEG
    (b"GIF89a",             "image/gif"),  # GIF 89a
    (b"GIF87a",             "image/gif"),  # GIF 87a
]


def _sniff_image_mime(header: bytes) -> str | None:
    """Return MIME type if header bytes match a known image signature, else None.

    Checks magic bytes rather than trusting the client-supplied Content-Type.
    WebP is detected by checking both the RIFF container header and the WEBP
    sub-header at byte offset 8.
    """
    for signature, mime in _IMAGE_SIGNATURES:
        if header[: len(signature)] == signature:
            return mime
    # WebP: b'RIFF' at offset 0, b'WEBP' at offset 8
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "image/webp"
    return None


def _safe_extension(filename: str) -> str | None:
    """Return the lowercased extension if it is in the allowlist, else None."""
    suffix = Path(filename).suffix.lower()
    return suffix if suffix in _ALLOWED_EXTENSIONS else None


# ── Upload endpoint ───────────────────────────────────────────────────────────


@router.post(
    "/upload",
    summary="Upload an image for a case study or insight",
    description=(
        "Accepts a single image file (JPEG, PNG, WebP, GIF). "
        "Validates file type via magic bytes (not just the claimed MIME type). "
        "Saves the file to the shared media/images folder with a UUID-based filename "
        "to prevent collisions and path-traversal attacks. "
        "Returns the persistent URL to store in image_url or hero_image. "
        "Requires X-Admin-Key header."
    ),
    dependencies=[Depends(_require_admin)],
)
async def upload_media(file: UploadFile) -> dict:
    """Upload an image and return its persistent URL path."""
    settings = get_settings()

    # ── 1. Validate file extension ─────────────────────────────────────────────
    original_name = file.filename or ""
    ext = _safe_extension(original_name)
    if ext is None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file extension. "
                f"Allowed: {', '.join(sorted(_ALLOWED_EXTENSIONS))}"
            ),
        )

    # ── 2. Read and validate file size ─────────────────────────────────────────
    max_bytes: int = settings.max_upload_bytes
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {max_bytes // (1024 * 1024)} MB.",
        )
    if not content:
        raise HTTPException(status_code=400, detail="Empty file.")

    # ── 3. Validate actual content via magic bytes ─────────────────────────────
    # Never trust client-supplied Content-Type or filename extension alone.
    if _sniff_image_mime(content[:12]) is None:
        raise HTTPException(
            status_code=400,
            detail="File content does not match a supported image format.",
        )

    # ── 4. Persist to shared media directory ──────────────────────────────────
    images_dir = Path(settings.media_root) / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # UUID filename prevents collisions and path-traversal via original name.
    filename = f"{uuid.uuid4()}{ext}"
    dest = images_dir / filename
    dest.write_bytes(content)

    url = f"{settings.media_url}/images/{filename}"
    LOGGER.info("Media upload: %r → %s (%d bytes)", original_name, url, len(content))
    return {"url": url, "filename": filename}
