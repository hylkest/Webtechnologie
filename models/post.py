class Post:
    def __init__(self, id, user_id, media_type, media_path, caption, created_at):
        self.id = id
        self.user_id = user_id
        self.media_type = media_type
        self.media_path = media_path
        self.caption = caption
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            media_type=row["media_type"],
            media_path=row["media_path"],
            caption=row["caption"],
            created_at=row["created_at"]
        )
