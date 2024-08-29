import streamlit as st
import msal
import requests

import os
from dotenv import load_dotenv

if os.getenv('AZURE_ENVIRONMENT') == 'local':
    load_dotenv()
    REDIRECT_URI = 'http://localhost:8501'

else:
    REDIRECT_URI = 'https://cemadrag-c8cve3anewdpcdhf.southafricanorth-01.azurewebsites.net/'


TENANT_ID = os.getenv('WEBSITE_AUTH_AAD_ALLOWED_TENANTS')
CLIENT_ID = '29f43284-6d7d-4e00-ad65-40a31b9ad7ab'
CLIENT_SECRET = os.getenv('MICROSOFT_PROVIDER_AUTHENTICATION_SECRET')

AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
SCOPE = ["User.Read"]


app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)

def get_auth_url():
    auth_url = app.get_authorization_request_url(SCOPE, redirect_uri=REDIRECT_URI)
    return auth_url


def get_token_from_code(auth_code):
    app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)
    result = app.acquire_token_by_authorization_code(auth_code, scopes=SCOPE, redirect_uri=REDIRECT_URI)
    return result['access_token']


def get_user_info(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    return response.json()


def handle_redirect():
    if not st.session_state.get('access_token'):
        code = st.experimental_get_query_params().get('code')
        if code:
            access_token = get_token_from_code(code)
            st.session_state['access_token'] = access_token
            st.experimental_set_query_params()