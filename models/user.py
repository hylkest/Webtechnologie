class User:
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password=row["password"]
        )
