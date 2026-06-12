from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.capture_route import router
from routes.context_pack_route import router as context_router


from database.db import migrate_db
from services.background_capture import background_capture_manager


app = FastAPI()
app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


@app.on_event("startup")
def on_startup():
    migrate_db()
    background_capture_manager.start()


app.include_router(router)

app.include_router(context_router)