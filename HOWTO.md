# pharmaco-backend

**Here are some descriptions for new developers who are interns and juniors to look into this and understand how to work and overcome their problems.**

# Visit Our Blogs: https://blog.repliq.dev/

# Project Structure
    Please go through this step to understand the structure

    models.py
    rest->
        serializers
        views
        urls
    
# Import order to follow while creating a new PR
    Python std library 
    django
    rest_framework
    third-party 

    All imports should be in ascending order

    For Example:

        Bad code:
            from rest_framework.test import APIClient
            from django.test import TestCase
            from rest_framework import status
            from weapi.rest.tests import testURLs
            from weapi.rest.tests import payloads
            from accountio.choices import OrganizationUserRole, OrganizationStatus
            from rest_framework.test import APIClient
            from django.contrib.auth import get_user_model
            from weapi.rest.tests import payloads, testURLs


        Good Code:
            from django.contrib.auth import get_user_model
            from django.test import TestCase

            from rest_framework import status
            from rest_framework.test import APIClient

            from accountio.choices import OrganizationStatus, OrganizationUserRole

            from weapi.rest.tests import payloads, testURLs


# Use Black Formatter and Isort
    Install packages
    Add it to your code editor 
    Click (ctrl+s) -- on your changes file

# Url naming conventions
    The url name should start with the plural form of the app name.
    Example:
        organizations.product-list not organization.product-list
        organizations.product-detail not organization.product-detail

# Github PR
    while creating pull request:
        Enter details with work flow
        PR should have below 10 files.
        Note that no migration files need to be pushed
        
# How to start work on a new Card
    Read the card details. Before starting work you should have a clear understanding of the work. Then  come up with a plan for how you'll do it.

# Problem solving guideline
    First use google 
    Think of the solution you got from Google and compare it to your problem. 
    If you're stuck, comment on your card with a description of the problem and refer someone to look into it.

# Private Organization Create
    An onboard organization should be created
    An organization user should be created
    set_default value must be set to == true
    Add the user as a staff member (for permission to manage IsOrganizationStaff)

    How to create organization user?
        Take a look at accountio.rest
            views (onboarding)
            serializer (onboarding)
            url (onboarding)

    When creating an onboarding organization it creates itself a user.