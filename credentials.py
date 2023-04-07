import random, string

random.seed(3)

username_chars = string.ascii_letters + string.digits
username_length = random.choice(range(5, 11))
password_length_per_type = random.choice(range(8, 21)) // 4

USERNAME = "".join(random.choice(username_chars) for _ in range(username_length))
EMAIL = USERNAME + "@email.com"

password_array = sum(
    [[random.choice(password_chars) for _ in range(password_length_per_type)]
    for password_chars in [
        string.ascii_lowercase,
        string.ascii_uppercase,
        string.digits,
        string.punctuation,
    ]],
    [],
)

random.shuffle(password_array)

PASSWORD = "".join(password_array)

if __name__ == "__main__":
    print("Username:", USERNAME)
    print("Email:", EMAIL)
    print("Password:", PASSWORD)