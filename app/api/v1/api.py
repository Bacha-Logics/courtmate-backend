from fastapi import APIRouter
from app.api.v1 import auth, users, cases, hearings, dashboard, documents, clients, admin, analytics, reminders

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(cases.router, prefix="/cases")
api_router.include_router(hearings.router, prefix="/hearings")# tags=["hearings"]-->is define in api.py file--> (router=APIRouter(tags=["Hearings"]) )
api_router.include_router(dashboard.router, prefix="/dashboard")
api_router.include_router(documents.router, prefix="/documents")
api_router.include_router(clients.router, prefix="/clients")
api_router.include_router(admin.router, prefix="/admin")
api_router.include_router(analytics.router, prefix="/analytics")
api_router.include_router(reminders.router, prefix="/reminders")





