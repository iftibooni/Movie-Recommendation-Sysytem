import streamlit as st
import pandas as pd
import hashlib
import pickle

# Load the movies list from the .pkl file
def load_movies_list():
    try:
        with open('movies.pkl', 'rb') as file:
            movies_list = pickle.load(file)
        return movies_list
    except FileNotFoundError:
        st.error('Movies list file not found.')
        return pd.DataFrame(columns=['Title', 'Type', 'Genre', 'Language', 'Origin', 'Director', 'Cast', 'Rating'])

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to load user data
def load_user_data():
    try:
        return pd.read_csv('users.csv', index_col=0)
    except FileNotFoundError:
        return pd.DataFrame(columns=['username', 'password'])

# Function to save user data
def save_user_data(users_df):
    try:
        users_df.to_csv('users.csv')
        st.success('User data saved successfully!')
    except Exception as e:
        st.error(f'Error saving user data: {str(e)}')

# Function to load user profiles
def load_profiles_data():
    try:
        return pd.read_csv('profiles.csv', index_col=0)
    except FileNotFoundError:
        return pd.DataFrame(columns=['username', 'tv_shows'])

# Function to save user profiles
def save_profiles_data(profiles_df):
    try:
        profiles_df.to_csv('profiles.csv')
        st.success('Profile data saved successfully!')
    except Exception as e:
        st.error(f'Error saving profile data: {str(e)}')

# Function to authenticate user
def authenticate(username, password, users_df):
    if username in users_df['username'].values:
        stored_password = users_df.loc[users_df['username'] == username, 'password'].values[0]
        return hash_password(password) == stored_password
    return False

# Load user data and profiles data
users_df = load_user_data()
profiles_df = load_profiles_data()

# Initialize session state for login and new TV shows
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''
    st.session_state['new_shows'] = []
    st.session_state['recommendations'] = pd.DataFrame()  # Initialize as empty DataFrame

# Load the movies list
movies_list = load_movies_list()

# Streamlit app
st.set_page_config(page_title='TV Show Recommender', page_icon=':tv:', layout='wide')

# Custom CSS for improved styling
st.markdown(
    """
    <style>
    body {
        background-color: #f0f0f0;
        color: #333333;
        font-family: Arial, sans-serif;
    }
    .streamlit-table {
        overflow: auto;
    }
    .streamlit-button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }
    .streamlit-button:hover {
        background-color: #45a049;
    }
    .login-container {
        max-width: 400px;
        padding: 20px;
        margin: auto;
        background-color: #ffffff;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
    }
    .login-title {
        text-align: center;
        font-size: 24px;
        margin-bottom: 20px;
    }
    .login-input {
        width: 100%;
        padding: 12px;
        margin: 8px 0;
        box-sizing: border-box;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    .login-button {
        background-color: #4CAF50;
        color: white;
        padding: 12px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        width: 100%;
    }
    .login-button:hover {
        background-color: #45a049;
    }
    .register-link {
        text-align: center;
        margin-top: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Login and Register Page
if st.session_state['logged_in']:
    st.subheader(f'Welcome {st.session_state["username"]}!')

    # Display user's profile
    user_profile = profiles_df[profiles_df['username'] == st.session_state['username']]
    if not user_profile.empty:
        st.header('Your Profile')
        tv_shows = user_profile.iloc[0]['tv_shows']
        if pd.isna(tv_shows):
            st.write('You have not added any TV shows yet.')
        else:
            st.subheader('TV Shows you are watching or liked:')
            for show in tv_shows.split(';'):
                show_details = show.split('|')
                if len(show_details) == 8:
                    show_card = f"""
                    **Title:** {show_details[0]}  
                    **Type:** {show_details[1]}  
                    **Genre:** {show_details[2]}  
                    **Language:** {show_details[3]}  
                    **Origin:** {show_details[4]}  
                    **Director:** {show_details[5]}  
                    **Cast:** {show_details[6]}  
                    **Rating:** {show_details[7]}
                    """
                    st.markdown(show_card)

    # Load the dataset for recommendations
    df = pd.read_csv('Final Dataset 2.csv', encoding='latin1')

    # Load the cosine similarity matrix
    cosine_sim_df = pickle.load(open('similarity.pk1', 'rb'))

    st.header('Get TV Show Recommendations')

    # Select a TV show title from the list
    selected_title = st.selectbox('Select a TV show title:', movies_list['Title'])

    if st.button('Get Recommendations'):
        # Function to recommend similar TV shows based on input title
        # Function to recommend similar TV shows based on input title
            def recommend_tv_shows(title, cosine_sim_matrix, df, top_n=5):
                idx = df[df['Title'].str.lower() == title.lower()].index
                if len(idx) == 0:
                    return "TV show not found in the dataset. Please try another title."

                sim_scores = list(enumerate(cosine_sim_matrix[idx][0]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                sim_scores = (sim_scores[1:top_n+1])

                _indices = [i[0] for i in sim_scores]
                return df['Title'].iloc[_indices]

            # Show recommendations if input title is not empty
            if selected_title:
                recommendations = recommend_tv_shows(selected_title, cosine_sim_df.values, df)
                if isinstance(recommendations, str):
                    st.warning(recommendations)
                else:
                    st.session_state['recommendations'] = recommendations
                    st.success(f"Top Recommendations for '{selected_title}':")
                    st.table(recommendations)

    # Add new TV shows from recommendations
    if not st.session_state['recommendations'].empty:
        st.markdown('<hr>', unsafe_allow_html=True)
        st.header('Add a New TV Show')
        selected_movie = st.selectbox('Select a TV show from the recommendations:', st.session_state['recommendations'])

        if st.button('Add TV show'):
            selected_movie_details = movies_list[movies_list['Title'] == selected_movie].iloc[0]
            new_show = f"{selected_movie_details['Title']}|{selected_movie_details['Type']}|{selected_movie_details['Genre']}|{selected_movie_details['Language']}|{selected_movie_details['Origin']}|{selected_movie_details['Director']}|{selected_movie_details['Cast']}|{selected_movie_details['Rating']}"

            if not user_profile.empty and not pd.isna(tv_shows):
                existing_shows = [show.split('|')[0] for show in tv_shows.split(';')]
                if selected_movie in existing_shows:
                    st.error('This TV show is already in your list.')
                else:
                    st.session_state['new_shows'].append(new_show)
                    st.success(f'TV show "{selected_movie}" added to your session!')
            else:
                st.session_state['new_shows'].append(new_show)
                st.success(f'TV show "{selected_movie}" added to your session!')

    # Display TV shows added in the current session
    if st.session_state['new_shows']:
        st.markdown('<hr>', unsafe_allow_html=True)
        st.header('New TV Shows Added')
        for show in st.session_state['new_shows']:
            show_details = show.split('|')
            st.markdown('<div class="streamlit-card">', unsafe_allow_html=True)
            st.markdown(f"**Title:** {show_details[0]}", unsafe_allow_html=True)
            st.markdown(f"**Type:** {show_details[1]}", unsafe_allow_html=True)
            st.markdown(f"**Genre:** {show_details[2]}", unsafe_allow_html=True)
            st.markdown(f"**Language:** {show_details[3]}", unsafe_allow_html=True)
            st.markdown(f"**Origin:** {show_details[4]}", unsafe_allow_html=True)
            st.markdown(f"**Director:** {show_details[5]}", unsafe_allow_html=True)
            st.markdown(f"**Cast:** {show_details[6]}", unsafe_allow_html=True)
            st.markdown(f"**Rating:** {show_details[7]}", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Button to save TV shows
    if st.button('Save TV Shows'):
        if st.session_state['new_shows']:
            if not user_profile.empty:
                current_shows = user_profile.iloc[0]['tv_shows']
                if pd.isna(current_shows):
                    updated_shows = ';'.join(st.session_state['new_shows'])
                else:
                    updated_shows = current_shows + ';' + ';'.join(st.session_state['new_shows'])
                profiles_df.loc[profiles_df['username'] == st.session_state['username'], 'tv_shows'] = updated_shows
            else:
                new_profile = pd.DataFrame([[st.session_state['username'], ';'.join(st.session_state['new_shows'])]], columns=['username', 'tv_shows'])
                profiles_df = pd.concat([profiles_df, new_profile], ignore_index=True)
            save_profiles_data(profiles_df)
            st.success('TV shows saved successfully!')
            st.session_state['new_shows'] = []  # Clear the session state
        else:
            st.warning('No new TV shows to save.')

    # Button to delete TV shows
    if not user_profile.empty:
        st.markdown('<hr>', unsafe_allow_html=True)
        st.header('Delete TV Shows')
        tv_shows = user_profile.iloc[0]['tv_shows']
        if pd.isna(tv_shows):
            st.info('No TV shows to delete.')
        else:
            current_shows = tv_shows.split(';')
            show_titles = [show.split('|')[0] for show in current_shows]
            show_to_delete = st.selectbox('Select a TV show to delete:', show_titles)
            if st.button('Confirm Delete'):
                updated_shows = [show for show in current_shows if show.split('|')[0] != show_to_delete]
                updated_shows_str = ';'.join(updated_shows)
                profiles_df.loc[profiles_df['username'] == st.session_state['username'], 'tv_shows'] = updated_shows_str
                save_profiles_data(profiles_df)
                st.success(f'TV show "{show_to_delete}" deleted from your profile.')
                st.session_state['new_shows'] = []  # Clear the session state

    # Logout button
    if st.button('Logout'):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.session_state['new_shows'] = []
        st.session_state['recommendations'] = pd.DataFrame()  # Clear recommendations on logout
else:
    # Login or Register Form
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="login-title">Login or Register</h2>', unsafe_allow_html=True)
    choice = st.radio('Select an option:', ['Login', 'Register'])

    if choice == 'Login':
        st.markdown('<form>', unsafe_allow_html=True)
        username = st.text_input('Username', key="login-username")
        password = st.text_input('Password', type='password', key="login-password")
        if st.button('Login', key="login-button"):
            if authenticate(username, password, users_df):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.experimental_rerun()
            else:
                st.error('Invalid username or password')
        st.markdown('</form>', unsafe_allow_html=True)
    elif choice == 'Register':
        st.markdown('<form>', unsafe_allow_html=True)
        username = st.text_input('Choose a Username', key="register-username")
        password = st.text_input('Choose a Password', type='password', key="register-password")
        confirm_password = st.text_input('Confirm Password', type='password', key="register-confirm-password")
        if st.button('Register', key="register-button"):
            if password != confirm_password:
                st.error('Passwords do not match')
            elif username in users_df['username'].values:
                st.error('Username already exists')
            else:
                # Hash the password and save the new user
                hashed_password = hash_password(password)
                new_user = pd.DataFrame([[username, hashed_password]], columns=['username', 'password'])
                users_df = pd.concat([users_df, new_user], ignore_index=True)
                save_user_data(users_df)
                st.success('User registered successfully!')
        st.markdown('</form>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
