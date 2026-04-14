from fastapi import FastAPI, HTTPException
import httpx
import logging
import redis
import json
import uuid
import time
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

GITHUB_API = "https://api.github.com"
MAX_RETRIES = 3

# Redis connection
try:
    redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
    redis_client.ping()
    logger.info("Connected to Redis")
except Exception as e:
    logger.warning(f"Redis not available: {e}")
    redis_client = None


async def fetch_with_retry(client: httpx.AsyncClient, url: str, request_id: str) -> httpx.Response:
    timeout = httpx.Timeout(5.0, connect=2.0)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.debug("Calling GitHub API", extra={
                "request_id": request_id,
                "url": url,
                "attempt": attempt
            })
            response = await client.get(url, timeout=timeout)
            return response

        except httpx.TimeoutException:
            logger.warning("GitHub timeout during retry attempt", extra={
                "request_id": request_id,
                "attempt": attempt
            })

            if attempt == MAX_RETRIES:
                raise

            await asyncio.sleep(2 ** attempt)

        except httpx.RequestError as e:
            logger.warning("Retry attempt failed", extra={
                "request_id": request_id,
                "attempt": attempt,
                "error": str(e)
            })

            if attempt == MAX_RETRIES:
                raise

            await asyncio.sleep(2 ** attempt)


@app.get("/")
def root():
    logger.info("Health check endpoint called")
    return {"message": "API is running"}


@app.get("/{username}")
async def get_gists(username: str):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    url = f"{GITHUB_API}/users/{username}/gists"

    logger.info("Request started", extra={
        "request_id": request_id,
        "username": username
    })

    cached_data = None

    try:
        # Step 1: Check cache
        if redis_client:
            try:
                cached_data = redis_client.get(username)
                if cached_data:
                    logger.info("Cache hit", extra={
                        "request_id": request_id,
                        "username": username
                    })

                    duration = (time.time() - start_time) * 1000
                    logger.info("Request completed (cache)", extra={
                        "request_id": request_id,
                        "username": username,
                        "duration_ms": round(duration, 2)
                    })

                    return {"gists": json.loads(cached_data)}

                logger.info("Cache miss", extra={
                    "request_id": request_id,
                    "username": username
                })

            except Exception as e:
                logger.warning("Redis error", extra={
                    "request_id": request_id,
                    "username": username,
                    "error": str(e)
                })

        # Step 2: Call GitHub with retry
        async with httpx.AsyncClient() as client:
            response = await fetch_with_retry(client, url, request_id)

        logger.info("GitHub response received", extra={
            "request_id": request_id,
            "username": username,
            "status_code": response.status_code
        })

        if response.status_code == 404:
            logger.warning("User not found", extra={
                "request_id": request_id,
                "username": username
            })
            raise HTTPException(status_code=404, detail="User not found")

        if response.status_code != 200:
            logger.error("GitHub API error", extra={
                "request_id": request_id,
                "username": username,
                "status_code": response.status_code
            })
            raise HTTPException(status_code=500, detail="GitHub API error")

        gists = response.json()

        result = []
        for gist in gists:
            result.append({
                "id": gist["id"],
                "description": gist["description"] or "",
                "url": gist["html_url"]
            })

        # Step 3: Store in cache
        if redis_client:
            try:
                redis_client.setex(username, 300, json.dumps(result))
                logger.info("Stored in cache", extra={
                    "request_id": request_id,
                    "username": username
                })
            except Exception as e:
                logger.warning("Cache store failed", extra={
                    "request_id": request_id,
                    "username": username,
                    "error": str(e)
                })

        duration = (time.time() - start_time) * 1000
        logger.info("Request completed", extra={
            "request_id": request_id,
            "username": username,
            "result_count": len(result),
            "duration_ms": round(duration, 2)
        })

        return {"gists": result}

    except httpx.TimeoutException:
        logger.error("GitHub timeout", extra={
            "request_id": request_id,
            "username": username
        })

        if cached_data:
            logger.warning("Serving stale cache (timeout)", extra={
                "request_id": request_id,
                "username": username
            })
            return {"gists": json.loads(cached_data)}

        raise HTTPException(status_code=504, detail="GitHub timeout")

    except httpx.RequestError as e:
        logger.error("Network error", extra={
            "request_id": request_id,
            "username": username,
            "error": str(e)
        })

        if cached_data:
            logger.warning("Serving stale cache (network error)", extra={
                "request_id": request_id,
                "username": username
            })
            return {"gists": json.loads(cached_data)}

        raise HTTPException(status_code=500, detail="Failed to connect to GitHub")

    except HTTPException as e:
        raise e

    except Exception:
        logger.exception("Unexpected error", extra={
            "request_id": request_id,
            "username": username
        })

        if cached_data:
            logger.warning("Serving stale cache (unexpected error)", extra={
                "request_id": request_id,
                "username": username
            })
            return {"gists": json.loads(cached_data)}

        raise HTTPException(status_code=500, detail="Internal server error")