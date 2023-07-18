import streamlit as st
from admin.pages_ import users #, portfolios, scenarios, figures
from admin.config import env
import pymongo

# initialize db connection
mongo_db_url = st.secrets['MONGO_DB_URL']
@st.experimental_singleton
def init_connection():
    return pymongo.MongoClient(mongo_db_url)[env]

st.session_state['db'] = init_connection()

# define pages
PAGES = {
    'Users': users,
    # 'Portfolios': portfolios,
    # 'Scenarios': scenarios,
    # 'Figures': figures
}

# disclaimer utility
def cleared_disclaimer():
    if 'cleared_disclaimer' not in st.session_state:
        st.session_state['cleared_disclaimer'] = None
    if st.session_state['cleared_disclaimer']:
        return True
    else:
        st.markdown('This admin panel UI is configured for: ')
        st.markdown(f'### {env} ###')
        st.markdown('Are you OK to proceed? If not please change the configuration variable in /admin')
        if st.button('Proceed'):
            st.session_state['cleared_disclaimer'] = True

# run main
def main():

    if cleared_disclaimer():
        # side bar: show pages
        st.sidebar.write(f'env: **{env}**')
        st.sidebar.write('---')
        page_selection = st.sidebar.radio("Page", list(PAGES.keys()), index=0)

        # run app of page requested
        page = PAGES[page_selection]
        page.app()

if __name__ == "__main__":
    main()