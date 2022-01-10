# import uvicorn
# from fastapi import FastAPI
# from fastapi_users.authentication import JWTAuthentication
#
#
# app = FastAPI()
#
#
# @app.get("/")
# def root():
#     return {"hello": "world"}
#
#
# SECRET = "SECRET"
#
# jwt_authentication = JWTAuthentication(
#     secret=SECRET, lifetime_seconds=3600, tokenUrl="auth/jwt/login"
# )
#
#
# if __name__ == "__main__":
#     uvicorn.run("main:app", reload=True, port=8001)

import uvicorn


def main():
    uvicorn.run(
        "core.app:app", host="0.0.0.0", port=8001, log_level="info", reload=True
    )


if __name__ == "__main__":
    main()
