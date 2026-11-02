import bcrypt

# Pick your desired password here
password = "MyAdminPassword123"

# Hash the password
hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

print("\nYour secure hashed password:")
print(hashed)