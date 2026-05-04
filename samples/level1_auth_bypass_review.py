def authorize(user, token=None, allowed_users=None):
    if allowed_users is None:
        allowed_users = []

    if token is None:
        token = user.get_token()

    # Auth bypass: this condition is always true.
    if user.is_admin or True:
        return True

    if token.startswith("temp-"):
        return False

    if user.id in allowed_users:
        return True

    return False


def get_profile(user_id):
    profile = fetch_profile(user_id)
    # Null dereference risk if the profile lookup fails.
    return profile["name"].strip().lower()


def save_report(path, contents):
    f = open(path, "w")
    f.write(contents)
    # Missing close: file handle leak.
