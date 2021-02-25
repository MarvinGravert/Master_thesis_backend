"""
Generate the protocol buffer code for python from proto files located in the
protos file. For each file create own folder
Adjust the import statements
"""
import glob
import re
from grpc_tools import protoc
from os import mkdir
from itertools import chain
# assume all code protocol buffers are in protos


def generate_proto_code():
    """
    Generates proto code and returns list of file names
    Return: list of file names
    """
    """
    Get file names
    """
    file_path_list = list()
    file_name_list = list()
    for file_path in glob.iglob("./protos/*.proto"):
        file_path_list.append(file_path)
        isolated_file_name = file_path.split("/")[2].split(".")[0]
        file_name_list.append(isolated_file_name)
    """
    Create Folder
    based on filename
    """
    folder_name = "protodef_files"
    try:
        mkdir(folder_name)
    except FileExistsError:
        pass

    """
    Generate the code into the folder
    """
    for file_path, file_name in zip(file_path_list, file_name_list):
        protoc.main([
            'grpc_tools.protoc',
            '--proto_path=protos',
            f'--python_out={folder_name}',
            f'--grpc_python_out={folder_name}',
            file_path])


if __name__ == "__main__":
    print(generate_proto_code())
