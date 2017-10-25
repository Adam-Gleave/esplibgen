#!/usr/bin/python

import sys
import json
import os

HEAD_COMMENT = "/*\n * esplibgen\n * Copyright 2017 Adam Gleave\n *\n * This file is part of esplibgen.\n" \
               " * esplibgen is free software, under the terms of the GPLv3 license.\n" \
               " * See the license file for more details.\n *\n */"

GEN_COMMENT = "\n\n/*\n * THIS CODE IS GENERATED VIA A PYTHON SCRIPT. \n" \
              " * DO NOT EDIT ANY OF THE CONTENTS OF THIS FILE" \
              " UNLESS IT IS SPECIFIED AS POSSIBLE.\n */\n\n"

def main(argv):
    input_path = str(os.path.dirname(os.path.abspath(__file__)))
    output_path = str(os.path.dirname(os.path.abspath(__file__)))

    try:
        input_path = input_path + "\\" + argv[1]
        output_path = output_path + "\\" + argv[2]

        if not os.path.exists(output_path):
            os.makedirs(output_path)

    except IndexError:
        print("Please specify an input file and output directory.")
        return

    try:
        input_json = open(input_path)
        input_string = input_json.read()
        items = []

        for i in range(len(json.loads(input_string)['ESP']['forms'])):
            item = json.loads(input_string)['ESP']['forms'][i]
            items.append(item)

        gen_classes(process_list(items), output_path)
    except FileNotFoundError:
        print("Input file not found: " + input_path)
        return


def process_list(items):
    class_list = []

    for i in range(0, len(items)):
        json_dict = items[i]
        class_list.append(process_dict(json_dict))

    return class_list


def process_dict(json_dict):
    new_class = []
    class_name = str(json_dict['signature'])
    class_type = str(json_dict['type'])

    try:
        parent = str(json_dict['inherits'])
        inherits = " : public " + parent
        includes = "#include " + "\"" + parent.lower() + ".hpp" + "\"\n\n"
    except KeyError:
        inherits = ""
        includes = ""

    try:
        member_list = json_dict['members']

    except KeyError:
        member_list = get_subrecord_members(json_dict['subrecords'])

    new_class.append(class_name.lower() + ".hpp")
    new_class.append(includes + class_type + " " + class_name + inherits + "\n{\n"
                     + process_members(member_list) + "}")
    return new_class


def get_subrecord_members(subrecords):
    members = []
    subrecord_members = []

    for subrecord_num in range(0, len(subrecords)):
        try:
            subrecord_members.append((subrecords[subrecord_num]['def'])['members'])

        except KeyError:
            print("Members not found in subrecord definition.")

    for subrecord_num in range(0, len(subrecord_members)):
        for member_num in range(0, len(subrecord_members[subrecord_num])):
            members.append(subrecord_members[subrecord_num][member_num])

    return members


def process_members(member_list):
    members = ""

    try:
        members = members + "\nprivate:\n"

        for i in range(0, len(member_list)):
            member = member_list[i]
            member_type = member['type']
            member_name = member['name']

            members = members + "\t"
            members = members + member_type + " "
            members = members + member_name + ";"
            members = members + "\n"
    except KeyError:
        print("Members not found in record definition.")

    return members


def gen_classes(class_list, out_dir):
    for i in range(0, len(class_list)):
        class_inf = class_list[i]
        file_name = str(out_dir + class_inf[0])
        raw_data = HEAD_COMMENT + GEN_COMMENT + class_inf[1]
        file = open(file_name, "w+")
        file.write(raw_data)


if __name__ == "__main__":
    main(sys.argv)
