import pathlib
import img2pdf
import PySimpleGUI as sg
from configparser import ConfigParser
import os


def verify_folder_path(folder_path):
    folder_path = pathlib.Path(folder_path)
    if folder_path.is_dir():
        return True
    else:
        return False


def get_image_list(source_path):
    source_path = pathlib.Path(source_path)
    img_list = []
    for file in source_path.iterdir():
        if file.suffix.lower() in (".jpg", ".png") and file.is_file():
            img_list.append(str(file))

    return img_list


def create_pdf_from_images(img_list, save_path):
    save_file_name = pathlib.Path(save_path).joinpath("Image_to_pdf.pdf")

    # Check if there are any images in the source folder
    if len(img_list) == 0:
        sg.popup("There are no image files in the source folder")
        return

    if save_file_name.exists():
        answer = sg.popup_yes_no("pdf file with the same name already exists\n"
                                 "Do you want to overwrite it?")
        if answer == "No":
            return

    with open(save_file_name, "wb") as f:
        f.write(img2pdf.convert(img_list))

    sg.popup_ok(f"{save_file_name.name} created in\n"
                f"{save_path}")


def read_config_info(section, option):
    config = ConfigParser()
    config_file = pathlib.Path(os.getcwd()).joinpath("Image_to_pdf.ini")
    if not config_file.exists():
        config.add_section("settings")
        config.set("settings", "source", "")
        config.set("settings", "destination", "")
        with open(config_file, "w") as f:
            config.write(f)

    config.read(config_file)
    return config.get(section, option)


def write_config_info(section, option, value):
    config = ConfigParser()
    config_file = pathlib.Path(os.getcwd()).joinpath("Image_to_pdf.ini")
    config.read(config_file)
    config.set(section, option, value)

    with open(config_file, "w") as f:
        config.write(f)


def gui_layout():
    source_path = read_config_info("settings", "source")
    save_path = read_config_info("settings", "destination")
    sg.theme("Light Green")
    layout = [
        [sg.Text(f"Select the source folder where images are located")],
        [sg.Input(source_path, disabled=False, key="source_path"),
         sg.FolderBrowse()],
        [sg.Text("Select where you want the pdf file to be saved\n"
                 "The pdf file will be called Image_to_pdf.pdf")],
        [sg.Input(save_path, disabled=False, key="save_path"),
         sg.FolderBrowse()],
        [sg.Button("Create PDF", key="Create PDF", size=(10, 1)),
         sg.Button("Exit", size=(10, 1))],
        # [sg.Button("Test", key="Test")]
    ]

    return sg.Window("Images to PDF", layout)


def event_loop():
    window = gui_layout()

    while True:
        event, values = window.read()

        if event in (None, "Exit"):
            window.close()
            break

        if event == "Create PDF":
            source_path = values["source_path"]  # read values from input boxes
            save_path = values["save_path"]
            if source_path == "" or save_path == "":
                sg.popup("Please select a source and destination folder")
            elif not verify_folder_path(source_path):
                sg.popup("The source folder specified is invalid\n"
                         "Please select a valid folder")
            elif not verify_folder_path(save_path):
                sg.popup("The save folder specified is invalid\n"
                         "Please select a valid folder")
            else:
                write_config_info("settings", "source", source_path)
                write_config_info("settings", "destination", save_path)
                image_list = get_image_list(source_path)
                create_pdf_from_images(image_list, save_path)


def main():
    event_loop()


if __name__ == '__main__':
    main()
