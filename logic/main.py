import os
from zipfile import ZipFile
from shutil import copyfile, rmtree
from PyQt5.QtWidgets import QMessageBox
from subprocess import Popen

found_pc = False


def message(msg_type, msg):
    msg_window = QMessageBox()
    msg_window.setIcon(msg_type)
    msg_window.setText(msg)
    msg_window.setStandardButtons(QMessageBox.Ok)
    msg_window.show()
    msg_window.exec()


def search_pc(path, pc):
    global found_pc
    file_list = os.listdir(path)
    for i in file_list:
        if pc in file_list:
            found_pc = True
            pc_path = path + "/" + pc
            return pc_path
        else:
            try:
                new_path = path+"/"+i
                p = search_pc(new_path, pc)
                if found_pc is True:
                    return p
            except NotADirectoryError:
                pass


def get_approval(app_path, pc):
    file_list = os.listdir(app_path)
    for approval in file_list:
        if approval[:len(pc)] == pc and approval[-3:] == "pdf":
            return approval


def make_zip(productCode_list, printing_type):
    global found_pc
    pc_list = productCode_list.keys()
    dst_path = "Approvals/"
    src_path = "C:/GMC/" + printing_type + "/"
    os.mkdir("Approvals")
    for pc in pc_list:
        pc_path = search_pc(src_path, pc)
        found_pc = False
        approval = get_approval(pc_path + "/WFD/", pc)
        app_path = pc_path + "/WFD/" + approval
        copyfile(app_path, dst_path + approval)
    zip_folder = ZipFile("Approvals.zip", "w")
    approval_list = os.listdir("Approvals/")
    for i in approval_list:
        zip_folder.write("Approvals/"+i)
    rmtree("Approvals")


def make_folder(pc_list):
    #[['MKAC001', printing_type, style_num, sub_program, logo]]
    for pc in pc_list:
        src_path = "C:/GMC/" + pc[1]
        src_path += "/" + pc[0][:2]
        try:
            os.mkdir(src_path)
        except FileExistsError:
            pass
        if pc[3]:
            src_path += "/" + pc[0][2:4]
            try:
                os.mkdir(src_path)
            except FileExistsError:
                pass
        src_path += "/" + pc[0]
        rollback_folder = src_path
        try:
            os.mkdir(src_path)
            if pc[4]:
                os.mkdir(src_path + "/LOGO")
            src_path += "/WFD"
            os.mkdir(src_path)
            if pc[2] > 1:
                make_styles_folder(src_path, pc[2])
            try:
                copyfile("C:/GMC/Checklist.xlsx", src_path + "/Checklist_" + pc[0] + ".xlsx")
                # message(QMessageBox.Information, "Folder(s) created successfully")
            except FileNotFoundError:
                message(QMessageBox.Critical, "Checklist not found in C:/GMC path")
                rmtree(rollback_folder)
                return False
        except FileExistsError:
            message(QMessageBox.Warning, pc[0] + " folder already exist")
    return True


def make_styles_folder(src_path, styles_num):
    for i in range(1, styles_num + 1):
        if len(str(i)) == 1:
            os.mkdir(src_path + "/00" + str(i))
        elif len(str(i)) == 2:
            os.mkdir(src_path + "0" + str(i))
        elif len(str(i)) == 3:
            os.mkdir(src_path + str(i))


def open_product_code(product_code):
    srcs_list = ["C:/GMC/ARC_Thermal", "C:/GMC/Digital", "C:/GMC/Offset",
                 "C:/GMC/PFL", "C:/GMC/Woven"]
    path = ""
    for src_path in srcs_list:
        path = search_pc(src_path, product_code)
        if path != "" and path is not None:
            path += "/WFD"
            Popen('explorer ' + '"' + path.replace('/', '\\') + '"')
            global found_pc
            found_pc = False
            break
    if path == "" or path is None:
        message(QMessageBox.Critical, "Product Code not found")


#make_zip({"US29HNW00C": 11, "US29HNW00E": 1, "US29M9W006":1, "US29M9W008":1}, "Offset")
#make_folder([["US2900A", "PFL", 2, True, False], ["US2900B", "PFL", 3, True, False]])
#copy_checklist(["US29HNW00C", "US29HNW00E", "US29M9W006", "US29M9W008"], "Offset")
#open_product_code("ONBAMKV001".strip())
