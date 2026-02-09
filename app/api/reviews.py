from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.database import get_db
from app.schemas.schemas import ReviewCreate, ReviewResponse, ReviewFeed, ReviewCommentCreate, ReviewCommentResponse
from app.services import review_service
from app.auth.deps import get_current_user, check_role
from app.models.models import User

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/submit", response_model=ReviewResponse)
async def submit_review(
    stars: int = Form(...),
    text: str = Form(...),
    guest_name: Optional[str] = Form(None),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if stars < 1 or stars > 5:
        raise HTTPException(status_code=400, detail="Stars must be between 1 and 5")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Review text is required")

    image_urls = []
    for file in files:
        if file.content_type.startswith("image/"):
            url = review_service.save_upload_file(file)
            image_urls.append(url)

    review_data = ReviewCreate(stars=stars, text=text, guest_name=guest_name)
    user_id = current_user.id if current_user else None

    db_review = review_service.create_review(db, review_data, user_id, image_urls)

    # Return as response schema
    feed_single = review_service.get_reviews_feed(db, page=1, limit=1, current_user_id=user_id)
    return feed_single["reviews"][0]

@router.get("/feed", response_model=ReviewFeed)
def get_feed(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    return review_service.get_reviews_feed(db, page, limit, user_id)

@router.post("/{review_id}/like")
def like_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required to like reviews")

    is_liked = review_service.toggle_like_review(db, review_id, current_user.id)
    return {"is_liked": is_liked}

@router.post("/{review_id}/comment", response_model=ReviewCommentResponse)
def comment_on_review(
    review_id: int,
    comment_data: ReviewCommentCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not comment_data.text.strip():
        raise HTTPException(status_code=400, detail="Comment text is required")

    user_id = current_user.id if current_user else None
    db_comment = review_service.add_comment_to_review(db, review_id, comment_data, user_id)

    # Map to response
    full_name = db_comment.guest_name
    if current_user:
        full_name = current_user.full_name or current_user.email.split('@')[0]

    return {
        "id": db_comment.id,
        "user_id": db_comment.user_id,
        "text": db_comment.text,
        "created_at": db_comment.created_at,
        "guest_name": db_comment.guest_name,
        "full_name": full_name
    }

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(check_role(["admin"]))
):
    success = review_service.delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return None
