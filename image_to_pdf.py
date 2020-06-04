import pathlib
import img2pdf
import PySimpleGUI as sg
import os
import subprocess
from configparser import ConfigParser


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


def create_pdf_from_images(img_list, save_path, file_name):
    file_name = f"{file_name}.pdf"
    save_file_name = pathlib.Path(save_path).joinpath(file_name)

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
        config.set("settings", "filename", "ImageToPDF")
        config.set("settings", "chk_open_folder", "")
        config.set("settings", "chk_open_pdf", "")
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


def get_num_of_files(source_path, file_types):
    source_path = pathlib.Path(source_path)
    num_of_files = len([file for file in source_path.iterdir() if file.suffix.lower() in file_types])

    return num_of_files


def get_total_file_size(source_path, file_types):
    total_size = 0
    source_path = pathlib.Path(source_path)
    for file in source_path.iterdir():
        file = pathlib.Path(file)
        if file.suffix.lower() in file_types:
            total_size += os.path.getsize(file)

    total_size = total_size / 1024 ** 2

    # format the size to correct number of decimal places
    if int(total_size) < 10:
        total_size = round(total_size, 2)
    elif int(total_size) < 100:
        total_size = round(total_size, 1)
    else:
        total_size = int(total_size)

    return total_size


def open_save_folder(folder_path):

    try:
        folder_path = pathlib.Path(folder_path)
        subprocess.call(["cmd", r"/c", "start", r"/max", folder_path])
    except Exception as ex:
        sg.popup_ok(f"An error occured while trying to open folder\n"
                    f"{folder_path}\n"
                    f"Error - {ex}")


def open_pdf_file(file_path, file_name):
    file_name = f"{file_name}.pdf"
    file_path = pathlib.Path(file_path)
    file_path = file_path.joinpath(file_name)
    subprocess.Popen([file_path], shell=True)


def gui_layout():
    source_path = read_config_info("settings", "source")
    save_path = read_config_info("settings", "destination")
    file_name = read_config_info("settings", "filename")
    chk_open_folder = bool(read_config_info("settings", "chk_open_folder"))
    chk_open_pdf = bool(read_config_info("settings", "chk_open_pdf"))
    sg.theme("Light Green")

    images_frame = [
        [sg.Text(f"Select the source folder where images are located")],
        [sg.Input(source_path, disabled=False, enable_events=True, key="source_path"),
         sg.FolderBrowse()],
        [sg.Text("", size=(47, 1), key="num_of_images")]
    ]

    pdf_frame = [
        [sg.Text("Select the folder to save the PDF file in")],
        [sg.Input(save_path, disabled=False, key="save_path"),
         sg.FolderBrowse()],
        [sg.Text("Save as filename"),
         sg.Input(file_name, key="save_file_name", size=(38, 1))],
        [sg.Text("", size=(47, 1), key="pdf_size_label")],
    ]

    layout = [
        [sg.Frame("Images", images_frame)],
        [sg.Frame("PDF File", pdf_frame)],
        [sg.Checkbox("Open folder after pdf is created", key="chk_open_folder",
                     enable_events=True, default=chk_open_folder)],
        [sg.Checkbox("Open PDF file after creating it", key="chk_open_pdf",
                     enable_events=True, default=chk_open_pdf)],

        [sg.Button("Create PDF", key="Create PDF", size=(10, 1)),
         sg.Button("Exit", size=(10, 1))],
        # [sg.Button("Test", key="Test")]
    ]

    return sg.Window("Images to PDF", layout, finalize=True)


def event_loop():
    window = gui_layout()

    while True:
        event, values = window.read()

        # if event == "Test":
        #     open_pdf_file(f"C:/Users/hifas/Desktop/Resized")

        if event in (None, "Exit"):
            window.close()
            break

        if event == "chk_open_folder":
            if values["chk_open_folder"]:
                write_config_info("settings", "chk_open_folder", "1")
            else:
                # bool("") evaluates to False
                write_config_info("settings", "chk_open_folder", "")

        if event == "chk_open_pdf":
            if values["chk_open_pdf"]:
                write_config_info("settings", "chk_open_pdf", "1")
            else:
                write_config_info("settings", "chk_open_pdf", "")

        if event == "source_path":
            source_path = values["source_path"]
            if verify_folder_path(source_path):
                file_types = [".jpg", ".png"]
                num_files = get_num_of_files(source_path, file_types)
                total_size = get_total_file_size(source_path, file_types)
                message = f"There are {num_files} images in the selected folder"
                pdf_size_message = f"Estimated file size of PDF: {total_size} MB"
                window["num_of_images"].update(message)
                window["pdf_size_label"].update(pdf_size_message)

        if event == "Create PDF":
            source_path = values["source_path"]  # read values from input boxes
            save_path = values["save_path"]
            save_file_name = values["save_file_name"]
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
                write_config_info("settings", "filename", save_file_name)
                image_list = get_image_list(source_path)
                create_pdf_from_images(image_list, save_path, save_file_name)

                if values["chk_open_folder"]:
                    open_save_folder(save_path)

                if values["chk_open_pdf"]:
                    open_pdf_file(save_path, save_file_name)


def main():
    event_loop()


if __name__ == '__main__':
    main()

# todo

# fixme
# large image files cause crash. Use PIL thumbnail to reduce size
