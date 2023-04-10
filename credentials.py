import sys, random, string

seed = 9

def generate_username_and_password(seed = seed):
    random.seed(seed)
    username_length = random.choice(range(5, 11))
    password_length_per_type = random.choice(range(8, 21)) // 4
    username = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(username_length))
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
    password = "".join(password_array)
    return username, password

USERNAME, PASSWORD = generate_username_and_password()
EMAIL = USERNAME + "@email.com"

if __name__ == "__main__":
    if "--list-users" in sys.argv:
        for i in range(seed + 1):
            username = generate_username_and_password(i)[0]
            print(username)
    else:
        print("Username:", USERNAME)
        print("Email:", EMAIL)
        print("Password:", PASSWORD)