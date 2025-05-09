from PyQt6.QtWidgets import *
from PyQt6.QtCore import QRegularExpression, QTimer
from PyQt6.QtGui import QRegularExpressionValidator
from voting_app import *
import csv
import os


class Logic(QMainWindow, Ui_MainWindow):
    """
        Logic class for managing the voting application.

        This class inherits from QMainWindow and Ui_MainWindow. It handles user interactions, checks inputs,
        saves votes to a CSV file, and shows the voting results.

        Attributes:
            candidates (list[str]): A list of candidate names.
            error_message_color (str): CSS style for error messages.
            success_message_color (str): CSS style for success messages.
            csv_file (str): The name of the CSV file where votes are saved.
        """
    candidates: list[str] = ["Jane", "John"]
    error_message_color: str = "color: red;"
    success_message_color: str = "color: green;"
    csv_file: str = "votes.csv"

    def __init__(self) -> None:
        """
            Initializes the Logic class, sets up the user interface, creates a list of
            digit inputs, and links button clicks to their corresponding method.

            Attributes:
                self.digit_inputs: A list of QLineEdit widgets for digit inputs.
        """
        super().__init__()
        self.setupUi(self)

        self.digit_inputs: list = [
            self.input_first_digit, self.input_second_digit,
            self.input_third_digit, self.input_fourth_digit,
            self.input_fifth_digit
        ]

        self.set_validators()
        self.connect_buttons()

    def set_validators(self) -> None:
        """
            Sets input validators for the name and digit fields.

            This method applies regular expression validators to ensure that the user inputs are the valid ones.
        """
        name_validator = QRegularExpressionValidator(QRegularExpression("[a-zA-Z-']+"))
        self.input_first_name.setValidator(name_validator)
        self.input_last_name.setValidator(name_validator)

        digit_validator = QRegularExpressionValidator(QRegularExpression("[0-9]"))
        for digit_input in self.digit_inputs:
            digit_input.setValidator(digit_validator)

    def connect_buttons(self) -> None:
        """
            Connects button click events to their respective methods.

            This method links the UI buttons to their corresponding functions
            to handle user interactions.
        """
        self.vote_button.clicked.connect(self.process_vote)
        self.result_button.clicked.connect(self.show_results)

        self.input_first_name.textChanged.connect(self.clear_message)
        self.input_last_name.textChanged.connect(self.clear_message)

        for digit_input in self.digit_inputs:
            digit_input.textChanged.connect(self.clear_message)

    def process_vote(self) -> None:
        """
        Processes the user's vote by validating inputs and saving the vote.

        This method checks if the user has provided all necessary information, validates the voting
        ID, checks for duplicate votes, and saves the vote to a CSV file. It also displays a
        success message upon successful voting.
        """
        if not self.input_first_name.text():
            return self.show_message("Please provide the first name", self.error_message_color)
        first_name = self.input_first_name.text()

        if not self.input_last_name.text():
            return self.show_message("Please provide the last name", self.error_message_color)
        last_name = self.input_last_name.text()

        if not self.get_voting_id():
            return self.show_message("Please provide the voting ID", self.error_message_color)
        voting_id = self.get_voting_id()
        if len(voting_id) != 5:
            return self.show_message("Voting ID must be 5 digits", self.error_message_color)

        if not (self.first_candidate_button.isChecked() or self.second_candidate_button.isChecked()):
            return self.show_message("Please select a candidate to vote for", self.error_message_color)

        if self.check_duplicate_vote(voting_id):
            return self.show_message("This Voting ID has already been used", self.error_message_color)

        candidate: str = self.candidates[0] if self.first_candidate_button.isChecked() else self.candidates[1]

        self.save_vote(first_name, last_name, voting_id, candidate)
        self.clear_form()

        self.show_message(f"Thank you {first_name}! You voted for {candidate}!", self.success_message_color)
        QTimer.singleShot(5000, self.message_label.clear)

    def get_voting_id(self) -> str:
        """
            Retrieves the voting ID by concatenating the digit inputs.

            Returns:
                str: The concatenated voting ID from the digit input fields.
        """
        return ''.join([digit_input.text() for digit_input in self.digit_inputs])

    def save_vote(self, first_name: str, last_name: str, voting_id: str, candidate: str) -> None:
        """
            Saves the vote information to a CSV file.

            Args:
                first_name (str): The voter's first name.
                last_name (str): The voter's last name.
                voting_id (str): The voter's voting ID.
                candidate (str): The name of the candidate voted for.
        """
        try:
            if not os.path.exists(self.csv_file):
                with open(self.csv_file, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['First Name', 'Last Name', 'Voting ID', 'Voted'])

            with open(self.csv_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([first_name, last_name, voting_id, candidate])

        except Exception as e:
            QMessageBox.warning(self, "Saving Error", f"Error saving the vote: {e}")

    def check_duplicate_vote(self, voting_id: str) -> bool:
        """
            Checks if the voting ID has already been used.

            Args:
                voting_id (str): The voting ID to check.

            Returns:
                bool: True if the voting ID has been used, False otherwise.
        """
        try:
            if not os.path.exists(self.csv_file):
                return False

            with open(self.csv_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Voting ID'] == voting_id:
                        return True

        except Exception as e:
            QMessageBox.warning(self, "ERROR", f"Error checking duplicate vote: {e}")
            return False

    def get_candidate_stats(self) -> dict[str, int]:
        """
            Retrieves the current vote counts for each candidate.

            Returns:
                dict[str, int]: A dictionary with candidate names as keys and their vote counts as values.
        """
        stats = {candidate: 0 for candidate in self.candidates}
        try:
            if not os.path.exists(self.csv_file):
                return stats

            with open(self.csv_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Voted'] in stats:
                        stats[row['Voted']] += 1

        except Exception as e:
            QMessageBox.warning(self, "Candidate Stats Error", f"Error getting candidate stats: {e}")
        return stats

    def show_results(self) -> None:
        """
            Displays the current voting results in a message box.

            This method retrieves the vote counts for each candidate and shows them
            in a formatted message box.
        """
        stats = self.get_candidate_stats()
        result_message = (
            f"Current Vote Counts:\n"
            f"{self.candidates[0]}: {stats[self.candidates[0]]}\n"
            f"{self.candidates[1]}: {stats[self.candidates[1]]}"
        )
        QMessageBox.information(self, "Voting Results", result_message)

    def show_message(self, text: str, color: str) -> None:
        """
            Displays a message in the message label with the specified color.

            Args:
                text (str): The message text to display.
                color (str): The CSS style to apply to the message label.
        """
        self.message_label.setText(text)
        self.message_label.setStyleSheet(color)

    def clear_message(self) -> None:
        """
            Clears the message label text.

            This method is called to reset the message label when the user starts typing in the input
            fields.
        """
        self.message_label.clear()

    def clear_form(self) -> None:
        """
            Clears all input fields and resets the candidate selection.

            This method is called to reset the form after a vote has been processed.
        """
        for field in [self.input_first_name, self.input_last_name] + self.digit_inputs:
            field.clear()

        if self.candidate_button_group.checkedButton() is not None:
            self.candidate_button_group.setExclusive(False)
            self.candidate_button_group.checkedButton().setChecked(False)
            self.candidate_button_group.setExclusive(True)