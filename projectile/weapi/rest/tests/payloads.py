from common.base_orm import BaseOrmCallApi

from tagio.choices import TagCategory, TagStatus


base_orm = BaseOrmCallApi()


def login_new_user_payload():
    payload = {"phone": "+8801722222222", "password": "new123pass"}

    return payload


def organization_payload():
    payload = {
        "name": "Elon Corp",
        "kind": "kind-elon",
        "domain": "",
        "tax_number": 2233,
        "registration_no": 3214,
        "website_url": "",
        "blog_url": "http://www.abc.com",
        "linkedin_url": "http://www.abc.com",
        "instagram_url": "http://www.abc.com",
        "facebook_url": "http://www.abc.com",
        "twitter_url": "http://www.abc.com",
        "summary": "http://www.abc.com",
        "description": "http://www.abc.com",
    }

    return payload


def user_and_organization_payload():
    payload = {
        "first_name": "Bill",
        "last_name": "Gates",
        "phone": "+8801711112222",
        "organization_name": "Bill Corp.",
        "organization_domain": "bill-corp",
        "password": "new123pass",
        "retype_password": "new123pass",
    }

    return payload


def organization_address_payload(upazila_uid, district_uid, division_uid):
    return {
        "label": "Pilkhana",
        "house_street": "G/9, Zakir Hossain Road",
        "upazila_uid": upazila_uid,
        "district_uid": district_uid,
        "division_uid": division_uid,
        "country": "Bangladesh",
    }


def organization_user_payload():
    payload = {
        "role": "ADMIN",
        "first_name": "Mark",
        "last_name": "Zuckerburg",
        "phone": "+8801733333333",
        "password": "new123pass",
        "email": "",
    }
    return payload


def base_product_payload():
    payload = {
        "superadmin": base_orm.super_user(),
        "category": base_orm.category(),
        "dosage_form": base_orm.dosage_form(),
        "ingredient": base_orm.ingredient(),
        "manufacturer": base_orm.manufacturer(),
        "unit": "100",
        "brand": base_orm.brand(),
        "route_of_administration": base_orm.route_of_administration(),
        "medicine_physical_state": base_orm.medicine_physical_state(),
    }

    return payload


def create_customer_payload():
    payload = {
        "first_name": "Dipu",
        "last_name": "Kanu",
        "phone": "+8801311449836",
        "password": "123456pas",
        "email": "dipu@example.com",
    }
    return payload


def customer_login_payload():
    payload = {
        "phone": "+8801311449836",
        "password": "123456pas",
    }
    return payload


def customer_address_payload(upazila_uid, district_uid, division_uid):
    return {
        "label": "Zakir Hossain Playground",
        "house_street": "G/9, Zakir Hossain Road",
        "upazila_uid": upazila_uid,
        "district_uid": district_uid,
        "division_uid": division_uid,
        "country": "Bangladesh",
    }


def add_product_payload(product_slug):
    payload = {"product": product_slug, "quantity": 5}
    return payload


def customer_order_payload(address_uid, payment_method_uid):
    payload = {
        "address_uid": address_uid,
        "payment_method_uid": payment_method_uid,
    }
    return payload


def tag_payload():
    payload = {
        "category": TagCategory.PRODUCT,
        "name": "tag_1",
        "i18n":"test_tag",
        "status": TagStatus.ACTIVE,
    }

    return payload


def address_payload():
    address_json = {
        "uid": "",
        "label": "",
        "house_street": "",
        "upazila": "",
        "district": "",
        "division": "",
        "country": "",
    }
    return address_json


def user_naming_payload():
    payload = {
        "first_name": "Koushik",
        "last_name": "Ayan",
    }
    return payload
