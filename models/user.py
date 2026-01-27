class User:
    def __init__(self, id, username, email, password=None, bio="", profile_photo=None, wallet_hash=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.bio = bio
        self.profile_photo = profile_photo
        self.wallet_hash = wallet_hash

    @classmethod
    def from_row(cls, row):
        keys = set(row.keys())
        return cls(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password=row["password"] if "password" in keys else None,
            bio=row["bio"] if "bio" in keys else "",
            profile_photo=row["profile_photo"] if "profile_photo" in keys else None,
            wallet_hash=row["wallet_hash"] if "wallet_hash" in keys else None
        )
