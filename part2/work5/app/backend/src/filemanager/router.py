from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status

from .service import FileService
from ..config import settings

# base file router
router = APIRouter()

# temlpates with HTMLs
templates = Jinja2Templates(
    directory=settings.TEMPLATES_DIR,
)

# service with file managment's logic
file_service = FileService()


@router.get("/", response_class=HTMLResponse)
async def get_all_files(request: Request):
    files = file_service.get_all_names()

    return templates.TemplateResponse(
        "files.html",
        {
            "request": request,
            "files": files,
        },
    )


@router.get("/download/{name}")
async def get_by_name(name: str):
    return StreamingResponse(
        file_service.get_by_name(name),
        media_type=file_service.get_media_type_by_name(name),
    )


@router.post("/upload", response_class=RedirectResponse)
async def upload_file(files: list[UploadFile] = File(...)):
    file_service.upload_files(files=files)
    return RedirectResponse("/files", status_code=status.HTTP_302_FOUND)
