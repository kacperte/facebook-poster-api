from fastapi import APIRouter
from app.tasks import facebook_poster

router = APIRouter(prefix="/bot", tags=["bot"])


@router.post(
    path="/run",
    summary="Run function that send content to Facebook groups",
    description="This API call function that send content to Facebook groups - text and image.",
)
def send_content_to_fb_groups(
    login: str,
    password: str,
):
    groups_name = ["https://www.facebook.com/groups/1281302162058634"]

    facebook_poster(login=login, password=password, groups=groups_name)
