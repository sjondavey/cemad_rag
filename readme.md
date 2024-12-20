An implementation of the Regulations_RAG project specifically for the South African Currency and Exchange Control Manual for Authorised Dealers

## Web front end
The web front end uses Streamlit and has been coded to run on the Streamlit Community Cloud or in Azure (with logging and analytics persisted to Blob Storage)

### Azure
Azure is useful if you want to persist logs and user information. Streamlit Community Cloud does offer access to logs, but they are only available while the application is awake. As soon as it goes to sleep, the logs are lost.

Initially, I intended to use Azure Authentication Services. While some hooks for this may still exist in this code, it has not been used and will probably not work.

To run the Azure front end locally, run `streamlit run .\app.py azure` from the command line. From an Azure Web App, use the startup Command `python -m streamlit run app.py azure --server.port 8000 --server.address 0.0.0.0` under Settings / Configuration.

Given the overhead when establishing connections to various services in Azure (e.g. keyvault), this frontend makes use of environmental variables. You need the following variables:
```
OPENAI_API_KEY_CEMAD = '...'
DECRYPTION_KEY_CEMAD = '...'

BLOB_ACCOUNT_URL = '...'
CHAT_BLOB_STORE = '...'
BLOB_CONTAINER = '...'
```

When running locally, you need to create a `.env` file and use load_dotenv. In an Azure Web App, create the variables (Settings / Environment variables). Note that adding a variable feels like a two-step process: add it and then save the changes. When a variable is added, you also seem to need to redeploy the app, so it's easiest to create all the variables up front before your initial deployment.

### Streamlit
I make use of the secrets.toml file in a .streamlit folder. That file should look like this:
```
[openai]
OPENAI_API_KEY = "..."

[index]
decryption_key = '...'

[passwords]
user_name = "bcrypt encoded password"
```
Note there is no Blob store to log to when using Streamlit, but there is a really basic authorization step. I could not get a [more robust authentication method to work](https://github.com/mkhorasani/Streamlit-Authenticator/issues/99). If you don't want the password, change the line `setup_for_streamlit(True)` in app.py to `setup_for_streamlit(False)`.

