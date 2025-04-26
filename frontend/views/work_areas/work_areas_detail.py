from controllers import work_areas_controller

def show_area_details(area_id):
    controller = work_areas_controller
    area = controller.get_by_id(area_id)
    if area:
        print("=== Work Area Details ===")
        for k, v in area.items():
            print(f"{k}: {v}")
    else:
        print("Area not found.")

if __name__ == '__main__':
    show_area_details(1)
