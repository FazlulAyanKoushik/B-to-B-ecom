def user_registration_payload():
    payload = {
        "first_name": "Saifullah",
        "last_name": "Shahen",
        "phone": "+8801752495467",
        "password": "new123pass",
        "email": "saifullah@example.com",
    }

    return payload


def password_reset_payload():
    payload = {
        "password": "new123pass",
        "new_password": "new123pass",
        "re_new_password": "new123pass",
    }

    return payload


def login_info_payload():
    payload = {"phone": "+8801711112222", "password": "new123pass"}

    return payload


def organization_user_payload():
    return {
        "first_name": "Mark",
        "last_name": "Zukarburg",
        "phone": "+8801309192698",
        "password": "newmark123pass",
        "email": "abcd@gmail.com",
        "role": "OWNER",
    }


def organization_registration_payload():
    return {
        "first_name": "Zakir",
        "last_name": "Hossain",
        "phone": "+8801710111213",
        "organization_name": "Zakir Corp",
        "organization_domain": "zakir-corp",
        "password": "Pass1234",
        "retype_password": "Pass1234",
    }


def organization_user_login_payload():
    return {"phone": "+8801710111213", "password": "Pass1234"}
