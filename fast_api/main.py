from fastapi import FastAPI
from fast_api.user_auth import app as auth_router
from fast_api.cluster import router as cluster_router  

app = FastAPI()

# Include routes
app.include_router(auth_router, prefix="/auth")
app.include_router(cluster_router, prefix="/cluster")

