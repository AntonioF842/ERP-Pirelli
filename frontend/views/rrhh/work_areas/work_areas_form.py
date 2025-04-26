from controllers.work_areas_controller import WorkAreasController

def input_area_data():
    name = input("Area name: ")
    description = input("Description: ")
    status = input("Status: ")
    return {
        "name": name,
        "description": description,
        "status": status
    }

def add_area():
    controller = WorkAreasController()
    area_data = input_area_data()
    nueva = controller.add(area_data)
    print(f"New area created: {nueva}")

if __name__ == '__main__':
    add_area()