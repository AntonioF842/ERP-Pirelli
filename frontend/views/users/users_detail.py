from controllers import users_controller

def show_user_details(user_id):
    controller = users_controller
    user = controller.get_by_id(user_id)
    if user:
        print("=== User Details ===")
        for k, v in user.items():
            print(f"{k}: {v}")
    else:
        print("User not found.")

if __name__ == '__main__':
    show_user_details(1)
