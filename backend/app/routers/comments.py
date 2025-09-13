import asyncio
from litestar import Router, post, get, websocket
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
from litestar.params import Dependency
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .. import models, schemas, db, realtime

# Create router - Litestar uses Router instead of APIRouter
router = Router(path="/comments", route_handlers=[])

# Create comment
@post("/", response_model=schemas.CommentOut)
async def create_comment(
    comment: schemas.CommentCreate, 
    session: AsyncSession = Dependency(db.get_async_session)
) -> schemas.CommentOut:
    """
    Creates a new comment and broadcasts it to all connected WebSocket clients.
    """
    try:
        # Create new comment
        new_comment = models.Comment(**comment.model_dump())
        session.add(new_comment)
        await session.commit()
        await session.refresh(new_comment)

        # Broadcast to all connected WebSocket clients
        await realtime.comment_manager.broadcast(
            "comments",  # Room name
            "new_comment",  # Event type
            {
                "id": new_comment.id,
                "username": new_comment.username,
                "message": new_comment.message,
                # It's better to send a string representation for JSON serialization
                "created_at": new_comment.created_at.isoformat() if new_comment.created_at else None,
            }
        )

        return new_comment

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating comment: {str(e)}"
        )

# Get all comments
@get("/", response_model=list[schemas.CommentOut])
async def get_comments(
    skip: int = 0, 
    limit: int = 100,
    session: AsyncSession = Dependency(db.get_async_session)
) -> list[schemas.CommentOut]:
    """
    Retrieves a paginated list of comments.
    """
    try:
        result = await session.execute(
            select(models.Comment)
            .order_by(models.Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        comments = result.scalars().all()
        return comments
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching comments: {str(e)}"
        )

# WebSocket for live comments
@websocket("/ws")
async def websocket_endpoint(websocket: websocket) -> None:
    # Accept the WebSocket connection first
    await websocket.accept()

    # Connect to the comment manager
    await realtime.comment_manager.connect("comments", websocket)

    try:
        # The while True loop is generally not needed if you are only
        # using the WebSocket for server-to-client broadcasts.
        # The connection will stay open until either side closes it.
        # A simple pass or a client-initiated loop is more appropriate.
        # If you expect client messages, then a while loop is necessary.
        async for data in websocket.iter_bytes():
            # This loop will run for as long as the client sends data.
            # You can handle incoming messages here.
            print(f"Received data: {data}")

    except Exception as e:
        # The disconnect logic should be handled in a `finally` block
        # to ensure it's always called.
        print(f"WebSocket closed or error: {e}")
    finally:
        # Always disconnect the client when the loop breaks or an error occurs
        realtime.comment_manager.disconnect("comments", websocket)

# Register all routes with the router
router.register(create_comment)
router.register(get_comments)
router.register(websocket_endpoint)