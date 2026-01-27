class Post:
    def __init__(
        self,
        id,
        user_id,
        media_type,
        media_path,
        caption,
        created_at,
        title=None,
        post_hash=None,
        username=None,
        wallet_hash=None,
        like_count=0,
        liked_by_current_user=0,
    ):
        self.id = id
        self.user_id = user_id
        self.media_type = media_type
        self.media_path = media_path
        self.caption = caption
        self.created_at = created_at
        self.title = title
        self.post_hash = post_hash
        self.username = username
        self.wallet_hash = wallet_hash
        self.like_count = like_count
        self.liked_by_current_user = liked_by_current_user

    @classmethod
    def from_row(cls, row):
        keys = set(row.keys())
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            media_type=row["media_type"],
            media_path=row["media_path"],
            caption=row["caption"],
            created_at=row["created_at"],
            title=row["title"] if "title" in keys else None,
            post_hash=row["post_hash"] if "post_hash" in keys else None,
            username=row["username"] if "username" in keys else None,
            wallet_hash=row["wallet_hash"] if "wallet_hash" in keys else None,
            like_count=row["like_count"] if "like_count" in keys else 0,
            liked_by_current_user=row["liked_by_current_user"] if "liked_by_current_user" in keys else 0,
        )
