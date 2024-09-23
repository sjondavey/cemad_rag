import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
import platform
import bcrypt

import streamlit as st

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient

from regulations_rag.rerank import RerankAlgos
from regulations_rag.corpus_chat import ChatParameters
from regulations_rag.embeddings import  EmbeddingParameters

from cemad_rag.cemad_corpus_index import CEMADCorpusIndex
from cemad_rag.corpus_chat_cemad import CorpusChatCEMAD

DEV_LEVEL = 15
ANALYSIS_LEVEL = 25
logging.addLevelName(DEV_LEVEL, 'DEV')       
logging.addLevelName(ANALYSIS_LEVEL, 'ANALYSIS')       

logger = logging.getLogger(__name__)
logger.setLevel(ANALYSIS_LEVEL)

def _setup_blob_storage_for_logging(filename):
    account_url = "https://chatlogsaccount.blob.core.windows.net/"
    if st.session_state['use_environmental_variables']:
        chat_blob_store_key = os.getenv("CHAT_BLOB_STORE")
        connection_string = f"DefaultEndpointsProtocol=https;AccountName=chatlogsaccount;AccountKey={chat_blob_store_key};EndpointSuffix=core.windows.net"
        # Create the BlobServiceClient object using the connection string
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    else:
        tmp_credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url, credential=tmp_credential)

    container_name = "cemadtest01"
    st.session_state['output_file'] = blob_service_client.get_blob_client(container=container_name, blob=filename)
    # Check if blob exists, if not create an append blob
    try:
        st.session_state['output_file'].get_blob_properties()  # Check if blob exists
    except:
        # Create an empty append blob if it doesn't exist
        st.session_state['output_file'].create_append_blob()


def setup_for_azure(filename):

    if 'service_provider' not in st.session_state:
        st.session_state['service_provider'] = 'azure'

    # bypass keyvault and set up everything from environmental variables
    if "use_environmental_variables" not in st.session_state:
        st.session_state['use_environmental_variables'] = True 

    if st.session_state['use_environmental_variables']:
        load_dotenv()
        if 'openai_api' not in st.session_state:
            secret_name = "OPENAI_API_KEY_CEMAD"
            openai_api_key = os.getenv(secret_name)
            st.session_state['openai_client'] = OpenAI(api_key = openai_api_key)
        _setup_blob_storage_for_logging(filename)

    else: # use key_vault
        if 'key_vault' not in st.session_state:
            # https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python
            # When the app is running in Azure, DefaultAzureCredential automatically detects if a managed identity exists for the App Service and, if so, uses it to access other Azure resources
            st.session_state['credential'] = DefaultAzureCredential() 
            st.session_state['key_vault'] = "https://cemadragkeyvault.vault.azure.net/"

            # Determine if the app is running locally or on Azure. When run locally, DefaultAzureCredential will default to 
            # environmentcredential and will pull the values AZURE_CLIENT_ID, AZURE_TENANT_ID and AZURE_CLIENT_SECRET from the
            # .env file 
            if os.getenv('AZURE_ENVIRONMENT') == 'local':
                st.session_state['app_path'] = "http://localhost:8501"

                # Load local .env file for credentials
                load_dotenv()
                if st.session_state['log_locally']:
                    folder_to_write_to = "./user_data"
                    # Ensure the folder exists
                    os.makedirs(folder_to_write_to, exist_ok=True)            
                    st.session_state['output_file'] = os.path.join(folder_to_write_to, filename)
                else:            
                    _setup_blob_storage_for_logging(filename)

            else: # folder in Azure
                st.session_state['app_path'] = "https://cemadrag-c8cve3anewdpcdhf.southafricanorth-01.azurewebsites.net"
                _setup_blob_storage_for_logging(filename)


        if 'openai_api' not in st.session_state:
            secret_client = SecretClient(vault_url=st.session_state['key_vault'], credential=st.session_state['credential'])
            api_key = secret_client.get_secret(secret_name)
            st.session_state['openai_client'] = OpenAI(api_key = api_key.value)


    if not "password_correct" in st.session_state: # No passwords yet in Azure but passwords required for other pages
        st.session_state["password_correct"] = True

def setup_for_streamlit(insist_on_password = False):
    if 'service_provider' not in st.session_state:
        st.session_state['service_provider'] = 'streamlit'

    # test to see if we are running locally or on the streamlit cloud
    if 'app_path' not in st.session_state:
        test_variable = platform.processor()
        if test_variable: # running locally
            st.session_state['app_path'] = "http://localhost:8501"
        else: # we are on the cloud
            st.session_state['app_path'] = "https://exconmanualchat.streamlit.app/"

    if 'output_folder' not in st.session_state:
        st.session_state['output_folder'] = "./user_data/"

    if 'openai_api' not in st.session_state:
        st.session_state['openai_client'] = OpenAI(api_key = st.secrets['openai']['OPENAI_API_KEY'])

        if not insist_on_password:
            if "password_correct" not in st.session_state.keys():
                st.session_state["password_correct"] = True
        else:
            ## Password
            def check_password():
                """Returns `True` if the user had a correct password."""

                def login_form():
                    """Form with widgets to collect user information"""
                    with st.form("Credentials"):
                        st.text_input("Username", key="username")
                        st.text_input("Password", type="password", key="password")
                        st.form_submit_button("Log in", on_click=password_entered)

                def password_entered():
                    """Checks whether a password entered by the user is correct."""
                    pwd_raw = st.session_state['password']
                    if st.session_state["username"] in st.secrets[
                        "passwords"
                    ] and bcrypt.checkpw(
                        pwd_raw.encode(),
                        st.secrets.passwords[st.session_state["username"]].encode(),
                    ):
                        st.session_state["password_correct"] = True
                        logger.log(ANALYSIS_LEVEL, f"New questions From: {st.session_state['username']}")
                        del st.session_state["password"]  # Don't store the username or password.
                        del pwd_raw
                        st.session_state["user_id"] = st.session_state["username"] 
                        del st.session_state["username"]
                        
                    else:
                        st.session_state["password_correct"] = False

                # Return True if the username + password is validated.
                if st.session_state.get("password_correct", False):
                    return True

                # Show inputs for username + password.
                login_form()
                if "password_correct" in st.session_state:
                    st.error("😕 User not known or password incorrect")
                return False

            if not check_password():
                st.stop()


def load_data(service_provider):
    logger.log(ANALYSIS_LEVEL, f"*** Loading data for {st.session_state['user_id']}. Should only happen once")
    logger.debug(f'--> cache_resource called again to reload data')
    with st.spinner(text="Loading the excon documents and index - hang tight! This should take 5 seconds."):
        
        if service_provider == 'azure':
            if st.session_state['use_environmental_variables']:
                secret_name = "DECRYPTION_KEY_CEMAD"
                decrytion_key = os.getenv(secret_name)
                corpus_index = CEMADCorpusIndex(decrytion_key)
            else:
                secret_client = SecretClient(vault_url=st.session_state['key_vault'], credential=st.session_state['credential'])
                key = secret_client.get_secret(secret_name)
                corpus_index = CEMADCorpusIndex(key.value)
        elif service_provider == 'streamlit':
            key = st.secrets["index"]["decryption_key"]
            corpus_index = CEMADCorpusIndex(key)

        rerank_algo = RerankAlgos.LLM
        rerank_algo.params["openai_client"] = st.session_state['openai_client']
        rerank_algo.params["model_to_use"] = st.session_state['selected_model']
        rerank_algo.params["user_type"] = corpus_index.user_type
        rerank_algo.params["corpus_description"] = corpus_index.corpus_description
        rerank_algo.params["final_token_cap"] = 5000 # can go large with the new models

        embedding_parameters = EmbeddingParameters("text-embedding-3-large", 1024)
        chat_parameters = ChatParameters(chat_model = "gpt-4o", temperature = 0, max_tokens = 500)
        
        chat = CorpusChatCEMAD(openai_client = st.session_state['openai_client'],
                          embedding_parameters = embedding_parameters, 
                          chat_parameters = chat_parameters, 
                          corpus_index = corpus_index,
                          rerank_algo = rerank_algo,   
                          user_name_for_logging=st.session_state["user_id"])

        return chat


def write_data_to_output(text):
    if st.session_state['service_provider'] == 'azure':
        if os.getenv('AZURE_ENVIRONMENT') == 'local':            
            if st.session_state['log_locally']:
                # Write to the file
                with open(st.session_state['output_file'], 'a') as file:
                    file.write(text + "\n")
            else:
                st.session_state['output_file'].append_block(text + "\n")
        else:
            st.session_state['output_file'].append_block(text + "\n")