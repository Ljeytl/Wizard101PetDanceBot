import logging
import random
import time
import os # Moved import os to top
from typing import List, Tuple

from shared import Globals

import pyautogui
from image import Arrow, load_textures, generate_subicons, remove_duplicate_subicons, get_screenshot, locate, locate_and_get_center


turn = 0
refresh_rate = 7
moves = []
ARROW_TO_KEY = {
    Arrow.Up: 'up',
    Arrow.Down: 'down',
    Arrow.Left: 'left',
    Arrow.Right: 'right'
}


def load_application() -> None:
    logging.info("Loading application")
    load_textures()
    generate_subicons()
    remove_duplicate_subicons()
    # This failsafe isn't neccesary as I have built one in already.
    pyautogui.FAILSAFE = False
    logging.info("Finished loading")


def update_search() -> None:
    global moves, turn
    screen = get_screenshot()

    """
    # temporarily removing script functionality
    while len(moves) < turn + 3:
        moves.append(random.choice([arrow for arrow in Arrow]))

    """
    # tries to search using subicons
    for arrow in Arrow:
        for sub_icon in arrow_subicons[arrow.value]:
            # bounds = locate(sub_icon, screen, confidence=0.825)
            bounds = locate(sub_icon, screen, confidence=0.9)

            if bounds is not None:
                moves.append(arrow)
                time.sleep(0.15)  # let time pass for next
    # """

    if len(moves) == turn + 3:
        logging.debug(f"End of round {turn + 1}.")
        time.sleep(0.5)  # give time between finishing and entering keys
        input_moves(moves)
        time.sleep(1.75 + 0.10 * turn)  # wait for game to show next round
        moves = []
        turn += 1

    # there are only five rounds
    if turn == 5:
        time.sleep(1)  # allow time for thread in gui.py read value of turn
        logging.debug("turn now equals 5, triggering the failsafe")
        # pyautogui.moveTo(0, 0)
        turn = 0  # reset turn to zero in-case user wants to play again
        Globals.game_finished = True


def input_moves(input_arrows: List[Arrow]) -> None:
    for arrow in input_arrows:
        pyautogui.press(ARROW_TO_KEY[arrow])
        time.sleep(0.2)


class MouseMover():
    # This class handles mouse movements and clicks.
    # Many actions now use image recognition to find elements on screen.
    # If image recognition fails (e.g., buttons not found), you might need to:
    #   - Ensure the game's visual appearance matches the images in the 'assets' folder.
    #   - Adjust 'confidence' values in locate_and_get_center or pyautogui.locate... calls.
    #     Lower confidence (e.g., 0.7) is less strict but can cause errors.
    #     Higher confidence (e.g., 0.95) is stricter. Default is often 0.8 or 0.9.
    """No need to do error checking since the user will not have access to this class."""

    def __init__(self, locations: List[int], snacks: List[int]) -> None:
        self.locations = locations
        self.snacks = snacks
        self.mouse_delay = 0.15  # in seconds

    def choose_and_moveto_location(self) -> None:
        available_locations = [
            i for i, location in enumerate(self.locations) if location]
        available_locations = [
            0] if available_locations == [] else available_locations
        location_choice = random.choice(available_locations)

        location_images = ["WizardCity.png", "Kroktopia.png", "marleybone.png", "mooshu.png", "dragonspyre.png"]
        image_to_find = location_images[location_choice]
        image_path = f"assets/{image_to_find}"

        coords = locate_and_get_center(image_path, confidence=0.8)

        if coords:
            MouseMover.move_and_click(coords[0], coords[1], self.mouse_delay)
        else:
            logging.error(f"Location image {image_to_find} not found. Action not performed.")

    def choose_snack(self) -> int:
        # USER ACTION REQUIRED: Configure your preferred snacks here.
        # 1. Create PNG images of your preferred snacks.
        # 2. Place these images in the 'assets/snacks/' directory.
        # 3. Update the list below with the filenames of your snack images.
        #    The order determines priority (first image in the list is checked first).
        # Example: preferred_snack_image_files = ["my_favorite_snack.png", "another_good_one.png"]
        #
        # Placeholder for preferred snack images - user needs to create these in assets/snacks/
        # Example: "assets/snacks/mega_snack_example.png"
        logging.info("Note: Preferred snack image filenames are placeholders (e.g., 'mega_snack_example.png'). "
                     "Actual images need to be created by the user in the 'assets/snacks/' directory.")
        preferred_snack_image_files = ["mega_snack_example.png", "super_snack_example.png"]

        slot_template_image = "assets/feedpet_snackunselected.png"
        try:
            actual_slot_regions = list(pyautogui.locateAllOnScreen(slot_template_image, confidence=0.8))
        except pyautogui.ImageNotFoundException:
            actual_slot_regions = []

        if not actual_slot_regions:
            logging.warning("Could not locate snack slots visually using template. Falling back to random snack choice.")
            available_slots = [i for i, use_slot in enumerate(self.snacks) if use_slot]
            return random.choice(available_slots) if available_slots else -1

        actual_slot_regions.sort(key=lambda region: region.left)
        # Store a list of (index, region) for easier lookup
        indexed_slot_regions = list(enumerate(actual_slot_regions))

        for image_file in preferred_snack_image_files:
            preferred_image_path = f"assets/snacks/{image_file}"
            # Check if the preferred snack image even exists to avoid pyautogui error spam
            if not os.path.exists(preferred_image_path):
                logging.debug(f"Preferred snack image {preferred_image_path} not found. Skipping.")
                continue

            try:
                found_preferred_snacks = list(pyautogui.locateAllOnScreen(preferred_image_path, confidence=0.8))
            except pyautogui.ImageNotFoundException:
                found_preferred_snacks = []

            for pref_snack_region in found_preferred_snacks:
                pref_snack_center_x = pref_snack_region.left + pref_snack_region.width / 2
                pref_snack_center_y = pref_snack_region.top + pref_snack_region.height / 2

                for slot_index, slot_region in indexed_slot_regions:
                    # Check if the center of the preferred snack is within the bounds of the current slot region
                    if (slot_region.left <= pref_snack_center_x <= slot_region.left + slot_region.width and
                            slot_region.top <= pref_snack_center_y <= slot_region.top + slot_region.height):
                        # Check if this slot_index is enabled by the user and is valid
                        if slot_index < len(self.snacks) and self.snacks[slot_index]:
                            logging.info(f"Preferred snack {image_file} found in available slot {slot_index}.")
                            return slot_index
                        else:
                            logging.debug(f"Preferred snack {image_file} found in slot {slot_index}, but this slot is not enabled by the user.")
                        break # Found the slot for this preferred snack instance, move to next preferred snack image or instance

        logging.info("No user-enabled preferred snacks found. Falling back to random snack choice from available slots.")
        available_slots = [i for i, use_slot in enumerate(self.snacks) if use_slot]
        return random.choice(available_slots) if available_slots else -1

    @staticmethod
    def move_and_click(x: int, y: int, mouse_delay: float = 0.15) -> None:
        """Moves mouse to (x, y) in delay seconds and left clicks."""
        pyautogui.moveTo(x, y, mouse_delay)
        pyautogui.click()

    @staticmethod
    def press_right_side_button(mouse_delay: float = 0.15) -> None:
        """Presses PLAY in select level screen,
        NEXT after game finishes,
        and FEED PET in feed screen."""
        image_names = ["Play_lvlselected.png", "next.png", "startgame.png", "feedpet_snackselected.png"]
        for image_name in image_names:
            image_path = f"assets/{image_name}"
            coords = locate_and_get_center(image_path, confidence=0.8)
            if coords:
                MouseMover.move_and_click(coords[0], coords[1], mouse_delay)
                return

        logging.error("Right side button not found via image recognition. Action not performed.")

    @staticmethod
    def press_left_side_button(mouse_delay: float = 0.15) -> None:
        """Presses CANCEL in select level screen,
        FINISH in both feed screen and post fees screen."""
        image_names = ["cancel.png", "finish.png"]
        for image_name in image_names:
            image_path = f"assets/{image_name}"
            coords = locate_and_get_center(image_path, confidence=0.8)
            if coords:
                MouseMover.move_and_click(coords[0], coords[1], mouse_delay)
                return

        logging.error("Left side button not found via image recognition. Action not performed.")

    def press_snack(self, snack_index: int, mouse_delay: float = 0.15) -> None:
        """Clicks on the snack given the snack number (0-4)."""
        # Ensure snack_index is valid (0-4)
        if not 0 <= snack_index < 5:
            logging.error(f"Invalid snack_index: {snack_index}. Must be between 0 and 4.")
            return

        slot_image_path = "assets/feedpet_snackunselected.png"
        try:
            # Ensure pyautogui is available, it should be imported at the top of the file.
            found_slots = list(pyautogui.locateAllOnScreen(slot_image_path, confidence=0.8))
        except pyautogui.ImageNotFoundException:
            found_slots = []
        except Exception as e: # Catch other potential pyautogui errors
            logging.error(f"Error during pyautogui.locateAllOnScreen for snacks: {e}")
            found_slots = []

        if len(found_slots) <= snack_index:
            logging.warning(f"Not enough snack slots found via image recognition for index {snack_index}. Found {len(found_slots)}. Action not performed.")
            return

        # If enough slots are found by image recognition
        # Sort found_slots by their x-coordinate to ensure they are in left-to-right order
        sorted_slots = sorted(found_slots, key=lambda slot: slot.left)

        target_slot_box = sorted_slots[snack_index]

        center_x = target_slot_box.left + target_slot_box.width / 2
        center_y = target_slot_box.top + target_slot_box.height / 2
        # Use self.mouse_delay
        MouseMover.move_and_click(center_x, center_y, self.mouse_delay if mouse_delay == 0.15 else mouse_delay)


class KeyboardPresser():
    """No need to do error checking since the user will not have access to this class."""

    def __init__(self) -> None:
        pass

    def press_key(self, key: str) -> None:
        pyautogui.press(key)
