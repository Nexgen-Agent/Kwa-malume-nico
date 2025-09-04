import asyncio
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .. import models, schemas, db, realtime

router = APIRouter(prefix="/comments", tags=["Comments"])

# Create comment
@router.post("/", response_model=schemas.CommentOut)
async def create_comment(
    comment: schemas.CommentCreate, 
    session: AsyncSession = Depends(db.get_async_session)  # Use async session
):
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
                "created_at": new_comment.created_at.isoformat(),
            }
        )
        
        return new_comment
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating comment: {str(e)}")

# Get all comments
@router.get("/", response_model=list[schemas.CommentOut])
async def get_comments(
    skip: int = 0, 
    limit: int = 100,
    session: AsyncSession = Depends(db.get_async_session)
):
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
        raise HTTPException(status_code=500, detail=f"Error fetching comments: {str(e)}")

# WebSocket for live comments
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the WebSocket connection first
    await websocket.accept()
    
    # Connect to the comment manager
    await realtime.comment_manager.connect("comments", websocket)
    
    try:
        while True:
            # Keep connection alive and process messages
            data = await websocket.receive_text()
            
            # Optional: process incoming messages if needed
            # For example, clients could send ping messages or other commands
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        # Handle disconnection
        realtime.comment_manager.disconnect("comments", websocket)
    except Exception as e:
        # Handle other errors
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
        realtime.comment_manager.disconnect("comments", websocket)

# You'll also need to add this dependency function to your db.py:
"""
# In db.py
async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
"""
