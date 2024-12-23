from fastapi import FastAPI, HTTPException
from nakama import Client

app = FastAPI(
    title='Gift Grab API',
    description='Interact with Nakama gaming server with these api methods.',
    version="1.0.0",
    docs_url="/docs",   # Swagger UI endpoint
    redoc_url="/redoc"  # ReDoc endpoint
)


# # Initialize Nakama client
# nakama_client = nk_client(
#     server_key="defaultkey",
#     host="127.0.0.1",
#     port="7350",
#     ssl=False
# )

# @app.post("/login")
# async def login(email: str, password: str):
#     try:
#         session = await nakama_client.authenticate_email(
#             email=email,
#             password=password,
#             create=True
#         )
#         return {"token": session.token, "user_id": session.user_id}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @app.get("/player/{user_id}/stats")
# async def get_player_stats(user_id: str, token: str):
#     try:
#         # Create session from token
#         session = await nakama_client.session_restore(token)
        
#         # Get player stats from storage
#         result = await nakama_client.read_storage_objects(
#             session,
#             [{"collection": "game_data", "key": "player_stats", "user_id": user_id}]
#         )
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))