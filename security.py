#https://github.com/kevintupper/streamlit-auth-demo
#https://learn.microsoft.com/en-us/entra/msal/python/getting-started/client-applications
import streamlit as st
import msal
import requests

import os
from dotenv import load_dotenv

if os.getenv('AZURE_ENVIRONMENT') == 'local':
    load_dotenv()
    REDIRECT_URI = 'http://localhost:8501/'

else:
    REDIRECT_URI = 'https://cemadrag-c8cve3anewdpcdhf.southafricanorth-01.azurewebsites.net/'


TENANT_ID = os.getenv('WEBSITE_AUTH_AAD_ALLOWED_TENANTS')
CLIENT_ID = 'f2ca13cc-44e7-462a-b71a-6b093a24e3d0'
CLIENT_SECRET = os.getenv('MICROSOFT_PROVIDER_AUTHENTICATION_SECRET')

AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
SCOPE = ["User.Read"]

def create_msal_client():
    return msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)
    

def get_auth_url():
    print("security.get_auth_url")

    app = create_msal_client()
    auth_url = app.get_authorization_request_url(SCOPE, redirect_uri=REDIRECT_URI)
    print(f"auth_url: {auth_url}")
    return auth_url


def get_token_from_code(auth_code):
    app = create_msal_client()
    result = app.acquire_token_by_authorization_code(auth_code, scopes=SCOPE, redirect_uri=REDIRECT_URI)
    #return result['access_token']
    return result


def get_user_info(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    return response.json()


def handle_redirect():
    if not st.session_state.get('access_token'):
        query_params = st.query_params
        if 'code' in query_params: 
            auth_code = query_params["code"]
            result = get_token_from_code(auth_code)
            if "access_token" in result:
                print('SUCCESS')
                st.session_state['access_token'] = result["access_token"]
            else:
                st.error("Authentication failed. Please try again.")
        else:
            print('code not in query_parameters')
            # Show the sign-in button
            if st.button("Sign In"):
                auth_url = get_auth_url()
                st.write(f"[Click here to sign in]({auth_url})")