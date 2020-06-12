""" Helper functions to keep views clean """


#
def generate_user_data(form):
    """
    Access form for user data 
    Returns a user_data object 
    """
    username = form.username.data
    password = form.password.data
    email = form.email.data
    first_name = form.first_name.data
    last_name = form.last_name.data
    return {
        'username': username,
        'password': password,
        'email': email,
        'first_name': first_name,
        "last_name": last_name
    }
