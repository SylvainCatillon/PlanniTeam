from django.conf import settings
from django.contrib.auth import (
    SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY, get_user_model,
)
from django.contrib.sessions.backends.db import SessionStore
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def log_user_in(driver, server_url):
    """Log a user in using a selenium driver"""
    user_info = {
        "email": "user@test.com",
        "password": "test_user_password",
        "first_name": "Paul"}
    user = get_user_model().objects.create_user(**user_info)
    driver.get(server_url+reverse("accounts:login"))
    username = driver.find_element_by_name("username")
    username.send_keys(user_info["email"])
    password = driver.find_element_by_name("password")
    password.send_keys(user_info["password"])
    driver.find_element_by_xpath(
        "//input[@value='login']").click()
    # TODO: trouver une façon d'attendre d'être connecté
    # WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.ID, "myAccount")))
    return user

# def create_session_cookie(user):  # TODO retester cette possibilité de login: https://stackoverflow.com/questions/22494583/login-with-code-when-using-liveservertestcase-with-django
#     """
#     Create a session cookie to make Selenium tests with a logged user
#     :param user: a user to log in
#     :return: the cookie to add to the driver
#     """
#
#     # Create the authenticated session using the  user credentials
#     session = SessionStore()
#     session[SESSION_KEY] = user.pk
#     session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
#     session[HASH_SESSION_KEY] = user.get_session_auth_hash()
#     session.save()
#
#     # Create the cookie dictionary
#     cookie = {
#         'name': settings.SESSION_COOKIE_NAME,
#         'value': session.session_key,
#         'secure': False,
#         'path': '/',
#     }
#     return cookie
