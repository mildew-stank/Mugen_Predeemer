# TODO: auto refund if request name isn't found in the dictionary on refresh
# TODO: either save request list or auto refund all on close/end
# TODO: spellcheck the parsed request vs display names in dictionary for most probable match
# TODO: auto update request list with webhooks
# TODO: add option for fight automation by waiting for mugen.exe return code
# TODO: add option for unlimited redemptions per session

import sys
import os
import threading
import random

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QFileDialog,
    QMainWindow,
)

import predeemer
import mugen


class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()

        self.predeemer = None
        self.reward_id = ""
        self.list_dictionary = {}
        self.character_dictionary = {}
        self.stages = []

        uic.loadUi("base/manager.ui", self)
        self.action_export_fighter_names.triggered.connect(self.export_fighter_names)
        self.browse_button.clicked.connect(self.browse_path)
        self.start_button.clicked.connect(self.start_integration)
        self.requests_list.itemClicked.connect(self.on_item_clicked)
        self.refresh_list_button.clicked.connect(self.refresh_list)
        self.fight_button.clicked.connect(self.start_fight)
        self.refund_button.clicked.connect(self.refund_request)
        self.status_bar_label = QLabel()
        self.status_bar.addWidget(self.status_bar_label)
        self.status_bar.setStyleSheet("QStatusBar::item {border: None;}")
        self.show()

        self.load_data()
        if not os.path.exists("cache"):
            os.makedirs("cache")

    def export_fighter_names(self):
        path = self.mugen_path_input.text()
        try:
            character_select_set = mugen.get_select_character_set(self.motif_input.text(), path)
            self.character_dictionary = mugen.make_character_dictionary(character_select_set, path)
        except:
            self.status_bar.showMessage("ERROR: Unexpected directory", 5000)
            return
        with open("cache/fighters.txt", "w") as out_file:
            out_file.writelines([string + '\n' for string in self.character_dictionary.keys()])
        self.status_bar.showMessage("Exported to cache/fighters.txt", 5000)


    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not path:
            return
        self.mugen_path_input.setText(path)

    def start_integration(self):
        if self.start_button.text() == "End":
            try:
                self.predeemer.delete_custom_reward(self.reward_id)
            except:
                self.status_bar.showMessage("ERROR: Failed to delete delete reward", 5000)
            self.start_button.setText("Start")
            return

        access_token = self.access_token_input.text()
        path = self.mugen_path_input.text()
        amount = self.amount_spin_box.value()
        cost = self.cost_spin_box.value()
        is_one_per_user = self.action_one_redeem_per_user.isChecked()

        try:
            character_select_set = mugen.get_select_character_set(self.motif_input.text(), path)
            self.character_dictionary = mugen.make_character_dictionary(character_select_set, path)
            self.stages = mugen.get_stage_list(path)
        except:
            self.status_bar.showMessage("ERROR: Unexpected directory", 5000)
            return
        try:
            self.predeemer = predeemer.Predeemer("ah4yv3x5c0h7ma514krs9von6xwgm7", access_token)
        except:
            self.status_bar.showMessage("ERROR: Failed to initialize integration", 5000)
            return
        try:
            self.reward_id = self.predeemer.create_custom_reward("Mugen request", cost, 'Enter "NAME vs NAME"', False, amount, is_one_per_user,)
        except:
            self.status_bar.showMessage("ERROR: Failed to create reward", 5000)
            return

        self.refresh_list_button.setEnabled(True)
        self.fight_button.setEnabled(True)
        self.refund_button.setEnabled(True)
        self.start_button.setText("End")

    def start_fight(self):
        if not self.requests_list.currentItem():
            return

        request = self.requests_list.currentItem().text()[4:]
        character_names = request.split(" vs ")
        try:
            character_ids = self.parse_input(request)
        except:
            self.status_bar.showMessage("ERROR: Could not parse request", 5000)
            return
        wait_time = 0
        path = self.mugen_path_input.text()
        motif = self.motif_input.text()
        stage = random.choice(self.stages)

        if self.action_predictions.isChecked():
            wait_time = 30
            try:
                self.predeemer.create_prediction(request, character_names, wait_time)
            except:
                self.status_bar.showMessage("ERROR: Failed to create prediction", 5000)
                return
            self.status_bar_label.setText("Waiting on prediction...")
            self.fight_button.setEnabled(False)
            status_timer = threading.Timer(wait_time, self.on_prediction_end)
            status_timer.start()

        mugen_timer = threading.Timer(wait_time, mugen.run, [motif, character_ids, stage, path])
        mugen_timer.start()
        try:
            self.handle_redemption("FULFILLED")
        except:
            self.status_bar.showMessage("ERROR: Failed to fulfill reward", 5000)
        self.remove_entry()

    def on_prediction_end(self):
        self.status_bar_label.setText("")
        self.fight_button.setEnabled(True)

    def parse_input(self, user_input):
        parsed_input = user_input.lower().split(" vs ")
        if len(parsed_input) != 2:
            raise Exception("Did not find 2 fighters from input")
        parsed_input[0] = random.choice(self.character_dictionary[parsed_input[0]])
        parsed_input[1] = random.choice(self.character_dictionary[parsed_input[1]])

        return parsed_input

    def refund_request(self):
        if not self.requests_list.currentItem():
            return

        try:
            self.handle_redemption("CANCELED")
        except:
            self.status_bar.showMessage("ERROR: Failed to cancel reward", 5000)
        self.remove_entry()

    def remove_entry(self):
        selected_item = self.requests_list.currentItem().text()
        del self.list_dictionary[selected_item]
        self.requests_list.takeItem(self.requests_list.currentRow())

    def handle_redemption(self, status):
        selected_item = self.requests_list.currentItem().text()
        redemption_id = self.list_dictionary[selected_item][0]
        self.predeemer.update_redemption_status(self.reward_id, redemption_id, status)

    def refund_all(self):
        failures = 0

        for request in self.list_dictionary:
            try:
                self.predeemer.update_redemption_status(self.reward_id, request[0], "CANCELED")
            except:
                failures += 1
                
        if failures > 0:
            self.status_bar.showMessage(f"ERROR: Failed to issue {failures} refunds")

        self.list_dictionary.clear()
        self.requests_list.clear()

    def refresh_list(self):
        slot_number = 1
        data = self.predeemer.get_custom_reward_redemptions(self.reward_id)

        self.requests_list.clear()

        for entry in data["data"]:
            list_item = f"{slot_number:0>{2}}: {entry['user_input']}"
            self.list_dictionary.update({list_item: [entry["id"], entry["user_name"]]})
            self.requests_list.addItem(list_item)
            slot_number += 1

    def on_item_clicked(self, clicked):
        self.status_bar.showMessage(self.list_dictionary[clicked.text()][1], 3000)

    def load_data(self):
        try:
            with open("cache/data.cfg", "r") as in_file:
               settings = in_file.readline().split(",")
        except:
            return
        if len(settings) != 3:
            return
        self.mugen_path_input.setText(settings[0])
        self.motif_input.setText(settings[1])
        self.access_token_input.setText(settings[2])

    def save_data(self):
        with open("cache/data.cfg", "w") as out_file:
            path = self.mugen_path_input.text()
            motif = self.motif_input.text()
            token = self.access_token_input.text()
            out_file.write(f"{path},{motif},{token}")

    def closeEvent(self, event):
        self.save_data()


def main():
    app = QApplication(sys.argv)
    mugen_manager = GUI()
    app.exec_()


if __name__ == "__main__":
    main()
