#!/usr/bin/python

import sys
import json
import os
import collections

HEAD_COMMENT = "/*\n * esplibgen\n * Copyright 2017 Adam Gleave\n *\n * This file is part of esplibgen.\n" \
               " * esplibgen is free software, under the terms of the GPLv3 license.\n" \
               " * See the license file for more details.\n *\n */"

GEN_COMMENT = "\n\n/*\n * THIS CODE IS GENERATED VIA A PYTHON SCRIPT. \n" \
              " * DO NOT EDIT ANY OF THE CONTENTS OF THIS FILE" \
              " UNLESS IT IS SPECIFIED AS POSSIBLE.\n */\n\n"


# Entrance point to code
# Pass in console arguments (testing from test/test.py)
def main(argv):
    paths = set_paths(argv)
    json_string = get_json(paths[0])
    filenames = get_filenames(json_string, paths[1])
    classes_raw = gen_code(json_string)
    output_files(classes_raw, filenames)


# Set the paths from which to read and write files
def set_paths(argv):
    input_path = str(os.path.dirname(os.path.abspath(__file__)))
    output_path = str(os.path.dirname(os.path.abspath(__file__)))

    try:
        input_path = input_path + "\\" + argv[1]
        output_path = output_path + "\\" + argv[2]

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        return input_path, output_path

    except IndexError:
        print("Please specify an input file and output directory.")
        return


# Get a JSON string object from a specified input file
def get_json(input_path):
    try:
        input_json = open(input_path)
        input_string = input_json.read()

        return input_string

    except FileNotFoundError:
        print("Input file not found: " + input_path)


# Generate appropriate filenames from the JSON
def get_filenames(json_string, output_path):
    filenames = []

    for i in range(len(json.loads(json_string)['ESP']['forms'])):
        definition = json.loads(json_string)['ESP']['forms'][i]
        filename = output_path + str(definition['name']).lower() + ".hpp"
        filenames.append(filename)

    return filenames


# Generate a list of strings, one per output file, containing generated code
def gen_code(json_string):
    classes = []

    for i in range(len(json.loads(json_string)['ESP']['forms'])):
        definition = json.loads(json_string)['ESP']['forms'][i]
        class_raw = gen_classes_raw(definition)
        classes.append(class_raw)

    return classes


# Generate a code string for a particular JSON definition
def gen_classes_raw(definition):
    file_code = collections.OrderedDict((('head', HEAD_COMMENT + GEN_COMMENT),
                                         ('includes', gen_includes(definition)),
                                         ('namespace', "namespace ESP"),
                                         ('brace_0', "\n{\n\n"),
                                         ('additional_defs', ""),
                                         ('main_def', gen_class_raw(definition)),
                                         ('brace_1', "\n}\n")))

    file_raw = ""

    keys = list(file_code.keys())

    for i in range(0, len(file_code)):
        file_raw = file_raw + str(file_code[keys[i]])

    return file_raw


# Generate includes for a file using any object parents
def gen_includes(definition):
    includes = "\n"

    try:
        includes = "#include \"" + str(definition['inherits']).lower() + ".hpp\"\n\n"
        return includes

    except KeyError:
        return includes


# Generate a code string for a JSON class (or struct) definition
def gen_class_raw(definition):
    class_raw = ""
    class_dict = gen_class_dict(definition)

    keys = list(class_dict.keys())

    for i in range(0, len(class_dict)):
        class_raw = class_raw + str(class_dict[keys[i]])

    return class_raw


# Generate a dictionary object for a class, containing all relevant string data
def gen_class_dict(definition):
    class_dict = collections.OrderedDict((('declaration', gen_class_type(definition)),
                                          ('inherits', gen_inheritance(definition)),
                                          ('brace_0', "\n{\n\n"),
                                          ('public', ""),
                                          ('pub_members', ""),
                                          ('private', ""),
                                          ('prv_members', ""),
                                          ('brace_1', "\n}\n")))

    return class_dict


# Return a string with a class/struct declaration
# For example: "class TES4" or "struct HEDR" etc
def gen_class_type(definition):
    try:
        type_str = str(definition['type'])
        name_str = str(definition['name'])

        return type_str + " " + name_str

    except KeyError:
        print("Record does not have a type or name.")


# Return a code string representing inherited classes
# For example: " : public RecordHeader"
def gen_inheritance(definition):
    parent_str = ""

    try:
        parent_str = " : public " + str(definition['inherits']) + parent_str
        return parent_str

    except KeyError:
        return parent_str


# Save class code string to associated file
def output_files(classes_raw, filenames):
    for i in range(len(filenames)):
        file = open(filenames[i], "w+")
        file.write(classes_raw[i])


# Pass system arguments to main function
if __name__ == "__main__":
    main(sys.argv)
