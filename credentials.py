import random, string

random.seed(1)

username_chars = string.ascii_letters + string.digits
password_chars = string.ascii_letters + string.digits + string.punctuation
username_length = random.choice(range(5, 11))
password_length = random.choice(range(5, 11))

USERNAME = "".join(random.choice(username_chars) for _ in range(username_length))
EMAIL = USERNAME + "@email.com"
PASSWORD = "".join(random.choice(password_chars) for _ in range(password_length))

if __name__ == "__main__":
    print("Username:", USERNAME)
    print("Email:", EMAIL)
    print("Password:", PASSWORD)