#!/usr/bin/python

import sys
import json
import os


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
        items.append(json.loads(input_string))
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
    class_name = str(json_dict['name'])
    class_type = str(json_dict['type'])
    member_list = json_dict['members']
    new_class.append(class_name.lower() + ".hpp")
    new_class.append(class_type + " " + class_name + "\n{\n"
                     + process_members(member_list) + "}")
    return new_class


def process_members(member_list):
    members = ""

    try:
        public_members = member_list['public']
        members = members + "public:\n"

        for i in range(0, len(public_members)):
            member = public_members[i]
            member_type = member[0]
            member_name = member[1]

            members = members + "\t"
            members = members + member_type + " "
            members = members + member_name + ";"
            members = members + "\n"
    except KeyError:
        print("Either public or private members not found in definition.")

    try:
        public_members = member_list['private']
        members = members + "\nprivate:\n"

        for i in range(0, len(public_members)):
            member = public_members[i]
            member_type = member[0]
            member_name = member[1]

            members = members + "\t"
            members = members + member_type + " "
            members = members + member_name + ";"
            members = members + "\n"
    except KeyError:
        print("Either public or private members not found in definition.")

    return members


def gen_classes(class_list, out_dir):
    for i in range(0, len(class_list)):
        class_inf = class_list[i]
        file_name = str(out_dir + class_inf[0])
        raw_data = class_inf[1]
        file = open(file_name, "w+")
        file.write(raw_data)


if __name__ == "__main__":
    main(sys.argv)
