import streamlit as st
import json
from src.api.auth import get_password_hash
from fastapi.encoders import jsonable_encoder
from src.api.models.user import UserInDB


def app():

    # connect to db
    db = st.session_state['db']

    # list of users
    cursor = db["users"].find({})
    usernames = [u['username'] for u in cursor]

    # set view
    view = st.selectbox('Select operation', options=['View', 'Create', 'Delete'], index=0)
    st.markdown('---')
    st.markdown('  \n')
    st.markdown(f'### {view} ###')
    st.markdown('  \n')

    # render view
    if view == 'View':
        render_read_ui(db, usernames)
    elif view == 'Create':
        render_create_ui(db, usernames)
    elif view == 'Delete':
        render_delete_ui(db, usernames)


def render_read_ui(db, usernames):

    # select and get user
    username = st.selectbox('See user: ', options=usernames, index=0)
    user = db["users"].find_one({"username": username})

    # print info
    st.code(json.dumps(user, indent=4), language='python')


def render_create_ui(db, usernames):

    # submit document
    with st.form(key='new user form', clear_on_submit=True):

        # get inputs
        username = st.text_input('Insert username')
        pw = st.text_input('Insert password')

        # submit button
        submitted = st.form_submit_button("Submit")

        # apply logic after submission
        if submitted:
            # validate
            if username in usernames:
                st.error(f'Username {username} exists already; please choose another name')
                st.stop()
            else:
                # hash pw
                hashed_password = get_password_hash(pw)

                # create user model
                user = UserInDB(username=username, hashed_password=hashed_password)

                # write in db
                db["users"].insert_one(jsonable_encoder(
                    user))  # todo: how to update usernames at the top straight after a new user has been created?

                # print on screen
                st.success(f'User created with name {username} and pw {pw} !')

def render_delete_ui(db, usernames):

    # select and get user
    username = st.selectbox('Select user: ', options=usernames, index=0)

    # delete across collections
    query = {'username': username}
    if st.button('Delete'):
        db["users"].delete_one(query)

        # print on screen
        st.success(
            f'User {username} has been sucessfully deleted!')
