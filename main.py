import os
from app import app
import uvicorn


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))


# import os
# import asyncio
# from app import app
# from hypercorn.config import Config
# from hypercorn.asyncio import serve

# if __name__ == "__main__":
#     config = Config()
#     config.bind = [f"0.0.0.0:{os.getenv('PORT', 8000)}"]  # The address to bind to
#     config.workers = (
#         1  # Number of worker processes (check Hypercorn docs for more options)
#     )
#     config.lifespan = "auto"  # Lifespan setting ('auto', 'on', 'off')
#     # config.limit_concurrency = 10  # Max number of simultaneous connections, similar to Uvicorn's limit_concurrency

#     asyncio.run(serve(app, config))
