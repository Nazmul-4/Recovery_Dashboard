import bcrypt

password = input("Enter your password: ")

hashed = b"$2b$12$TejkeGxfYEC0qjJe2sV6gOaid2hJSmIgKW8oxLXzIPWytJRURxLBC"

result = bcrypt.checkpw(
    password.encode("utf-8"),
    hashed
)

print("Password correct:", result)