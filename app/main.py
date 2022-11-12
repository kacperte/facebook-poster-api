from fastapi import FastAPI
from .router import bot, user, material
from .db.database import engine
from .db import models


app = FastAPI()
app.include_router(bot.router)
app.include_router(material.router)
app.include_router(user.router)

models.Base.metadata.create_all(engine)
