import pathlib
import img2pdf
import PySimpleGUI as sg
from configparser import ConfigParser
import os


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


def read_config_info():
    config = ConfigParser()
    config_file = pathlib.Path(os.getcwd()).joinpath("Image_to_pdf.ini")
    if not config_file.exists():
        return "", ""

    config.read(config_file)

    source_path = config.get("settings", "source")
    save_path = config.get("settings", "destination")
    return source_path, save_path


def write_config_info(source_path, save_path):
    config = ConfigParser()
    config["settings"] = {
        "source": source_path,
        "destination": save_path
    }
    config_file = pathlib.Path(os.getcwd()).joinpath("Image_to_pdf.ini")
    with open(config_file, "w") as f:
        config.write(f)


def gui_layout():

    source_path, save_path = read_config_info()

    sg.theme("Light Green")
    layout = [
              [sg.Text(f"Select the source folder where images are located")],
              [sg.Input(source_path, disabled=True, key="source_path"),
               sg.FolderBrowse()],
              [sg.Text("Select where you want the pdf file to be saved\n"
                       "The pdf file will be called Image_to_pdf.pdf")],
              [sg.Input(save_path, disabled=True, key="save_path"),
               sg.FolderBrowse()],
              [sg.Button("Create PDF", key="Create PDF", size=(10, 1)),
               sg.Button("Exit", size=(10, 1))],
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
            source_path = values["source_path"]
            save_path = values["save_path"]
            if source_path == "" or save_path == "":
                sg.popup("Please select a source and destination folder")
            else:
                write_config_info(source_path, save_path)
                image_list = get_image_list(source_path)
                create_pdf_from_images(image_list, save_path)


def main():
    event_loop()


if __name__ == '__main__':
    main()
