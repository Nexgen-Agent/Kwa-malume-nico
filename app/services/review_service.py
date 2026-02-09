from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Review, ReviewLike, ReviewComment, ReviewImage, User
from app.schemas.schemas import ReviewCreate, ReviewCommentCreate
import os
import uuid
import shutil
from datetime import datetime
from typing import List, Optional

UPLOAD_DIR = "assets/images/reviews"

def create_review(db: Session, review_data: ReviewCreate, user_id: Optional[int] = None, image_urls: List[str] = []):
    db_review = Review(
        user_id=user_id,
        guest_name=review_data.guest_name if not user_id else None,
        stars=review_data.stars,
        text=review_data.text
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    for url in image_urls:
        db_image = ReviewImage(review_id=db_review.id, image_url=url)
        db.add(db_image)

    db.commit()
    db.refresh(db_review)
    return db_review

def get_reviews_feed(db: Session, page: int = 1, limit: int = 10, current_user_id: Optional[int] = None):
    offset = (page - 1) * limit

    total_count = db.query(func.count(Review.id)).scalar()

    query = db.query(Review).order_by(Review.created_at.desc()).offset(offset).limit(limit)
    reviews = query.all()

    results = []
    for review in reviews:
        # Count likes
        likes_count = db.query(func.count(ReviewLike.id)).filter(ReviewLike.review_id == review.id).scalar()

        # Count comments
        comments_count = db.query(func.count(ReviewComment.id)).filter(ReviewComment.review_id == review.id).scalar()

        # Check if liked by current user
        is_liked = False
        if current_user_id:
            is_liked = db.query(ReviewLike).filter(
                ReviewLike.review_id == review.id,
                ReviewLike.user_id == current_user_id
            ).first() is not None

        # Get reviewer name
        reviewer_name = review.guest_name
        if review.user:
            reviewer_name = review.user.full_name or review.user.email.split('@')[0]

        # Get comments
        comments = db.query(ReviewComment).filter(ReviewComment.review_id == review.id).all()
        comment_responses = []
        for c in comments:
            c_name = c.guest_name
            if c.user:
                c_name = c.user.full_name or c.user.email.split('@')[0]
            comment_responses.append({
                "id": c.id,
                "user_id": c.user_id,
                "text": c.text,
                "created_at": c.created_at,
                "guest_name": c.guest_name,
                "full_name": c_name
            })

        results.append({
            "id": review.id,
            "user_id": review.user_id,
            "stars": review.stars,
            "text": review.text,
            "created_at": review.created_at,
            "guest_name": review.guest_name,
            "likes_count": likes_count,
            "comments_count": comments_count,
            "is_liked": is_liked,
            "images": review.images,
            "comments": comment_responses,
            "full_name": reviewer_name
        })

    return {
        "reviews": results,
        "total_count": total_count,
        "page": page,
        "pages": (total_count + limit - 1) // limit
    }

def toggle_like_review(db: Session, review_id: int, user_id: int):
    existing_like = db.query(ReviewLike).filter(
        ReviewLike.review_id == review_id,
        ReviewLike.user_id == user_id
    ).first()

    if existing_like:
        db.delete(existing_like)
        db.commit()
        return False # Unliked
    else:
        new_like = ReviewLike(review_id=review_id, user_id=user_id)
        db.add(new_like)
        db.commit()
        return True # Liked

def add_comment_to_review(db: Session, review_id: int, comment_data: ReviewCommentCreate, user_id: Optional[int] = None):
    db_comment = ReviewComment(
        review_id=review_id,
        user_id=user_id,
        guest_name=comment_data.guest_name if not user_id else None,
        text=comment_data.text
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def delete_review(db: Session, review_id: int):
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if db_review:
        # Delete images from disk if they are local
        for img in db_review.images:
            if img.image_url.startswith("/" + UPLOAD_DIR):
                file_path = img.image_url.lstrip("/")
                if os.path.exists(file_path):
                    os.remove(file_path)

        db.delete(db_review)
        db.commit()
        return True
    return False

def save_upload_file(file):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/{file_path}"
