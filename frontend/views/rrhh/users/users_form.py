from controllers import users_controller

def input_user_data():
    username = input("Username: ")
    full_name = input("Full Name: ")
    email = input("Email: ")
    role = input("Role: ")
    status = input("Status: ")
    return {
        "username": username,
        "full_name": full_name,
        "email": email,
        "role": role,
        "status": status
    }

def add_user():
    controller = users_controller.UsersController()
    user_data = input_user_data()
    nuevo = controller.add(user_data)
    print(f"New user created: {nuevo}")

if __name__ == '__main__':
    add_user()
