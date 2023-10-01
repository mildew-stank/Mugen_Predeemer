import os
import subprocess


class Mugen:
    def __init__(self, path=os.getcwd()):
        self.path = path

    def get_character_folder_list(self):
        return os.listdir(f"{self.path}/chars")

    def get_stage_list(self):
        result = []
        files = os.listdir(f"{self.path}/stages")

        for file in files:
            if file.endswith(".def"):
                result.append(file[:-4])

        return result

    def get_select_character_set(self, motif):
        lines = list()
        characters = set()  # using a set instead of a list to avoid duplicates

        with open(f"{self.path}/data/{motif}/select.def", "r") as in_file:
            lines = in_file.readlines()

        for line in lines:
            parse_line = line.strip()
            if (
                not parse_line
                or parse_line[0] == ";"
                or parse_line == "randomselect"
                or parse_line == "-/"
                or parse_line == "[Characters]"
            ):  # ignore whitespace, comment lines, randomselect, blanks, and characters tag
                continue
            if parse_line[0] == "[":  # stop when a new tag begins
                break
            split_parse_line = parse_line.split(",")
            characters.add(split_parse_line[0])

        return characters

    def get_display_name(self, name):
        lines = []

        with open(f"{self.path}/chars/{name}/{name}.def", "r") as in_file:
            lines = in_file.readlines()

        for line in lines:
            parse_line = line
            if parse_line.startswith("displayname"):
                split_parse_line = parse_line.split('"')
                return split_parse_line[1]

        return False

    def make_character_dictionary(self, characters):
        # dictionary example: {"display name": ["id name 1", "id name 2"...]}
        character_dictionary = {}

        for character in characters:
            display_name = self.get_display_name(character).lower()
            if display_name in character_dictionary:
                character_dictionary[display_name].append(character)
                continue
            character_dictionary[display_name] = [character]

        return character_dictionary

    def run(self, motif, characters, stage):
        command = f"mugen.exe -r {motif} -p1.ai 1 {characters[0]} -p2.ai 1 {characters[1]} -s {stage}"
        subprocess.Popen(command, cwd=self.path, shell=True)
