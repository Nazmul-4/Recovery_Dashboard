import streamlit_authenticator as stauth

plain_password = "SAIful_VAI_@9418"
hashed_password = stauth.Hasher.hash(plain_password)

print("Hashed password:")
print(hashed_password)