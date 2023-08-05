import os
import subprocess


def get_character_folder_list(path=""):
    return os.listdir(f"{path}/chars")


def get_stage_list(path=""):
    result = []
    files = os.listdir(f"{path}/stages")

    for file in files:
        if file.endswith(".def"):
            result.append(file[:-4])

    return result


def get_select_character_set(motif=None, path=""):
    lines = list()
    characters = set()  # i'm using a set instead of a list to avoid duplicates

    with open(f"{path}/data/{motif}/select.def", "r") as in_file:  # TODO: error handling here and in get_display_name
        lines = in_file.readlines()

    for line in lines:
        parse_line = line.strip()
        if (
            not parse_line
            or parse_line[0] == ";"
            or parse_line == "randomselect"
            or parse_line == "[Characters]"
        ):  # ignore whitespace, comment lines, randomselect, and characters tag
            continue
        if parse_line[0] == "[":  # stop when a new tag begins
            break
        split_parse_line = parse_line.split(",")
        characters.add(split_parse_line[0])

    return characters


def get_display_name(name, path=""):
    lines = []

    with open(f"{path}/chars/{name}/{name}.def", "r") as in_file:
        lines = in_file.readlines()

    for line in lines:
        parse_line = line
        if parse_line.startswith("displayname"):
            split_parse_line = parse_line.split('"')
            return split_parse_line[1]

    return False


def make_character_dictionary(characters, path=""):
    # dictionary example: {"display name": ["id name 1", "id name 2"...]}
    character_dictionary = {}

    for character in characters:
        display_name = get_display_name(
            character, path
        ).lower()  # this makes it case insensitive
        if display_name in character_dictionary:
            character_dictionary[display_name].append(character)
            continue
        character_dictionary[display_name] = [character]

    return character_dictionary


def run(motif, characters, stage, path=""):
    command = (f"{path}/mugen.exe -r {motif} -p1.ai 1 {characters[0]} -p2.ai 1 {characters[1]} -s {stage}")
    subprocess.Popen(command, cwd=path, shell=True)
