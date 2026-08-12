from auth.users import USERS


def authenticate(email, password):

    email = email.strip().lower()

    for user in USERS:

        if (
            user["email"].lower() == email
            and
            user["password"] == password
        ):
            return user

    return None