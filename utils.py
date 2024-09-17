#https://github.com/kevintupper/streamlit-auth-demo

import streamlit as st
import security

def setup_page(page_title):
    print("utils.setup_page")

    st.set_page_config(
        page_title=page_title,
        page_icon="👋",
    )

    print(f'*******  st.query_params:')
    print(st.query_params)
    security.handle_redirect()
    # if st.query_params.get('code'):
    #     print("handling redirect")
    #     security.handle_redirect()

    access_token = st.session_state.get('access_token')

    if access_token:
        user_info = security.get_user_info(access_token)
        st.session_state['user_info'] = user_info
        return True
    else:
        st.write("Please sign-in to use this app.")
        auth_url = security.get_auth_url()
        st.markdown(f"<a href='{auth_url}' target='_self'>Sign In</a>", unsafe_allow_html=True)
        st.stop()