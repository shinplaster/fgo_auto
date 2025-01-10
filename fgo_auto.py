import argparse
import cv2
import logging
import numpy as np
import os
import pyautogui
import pyocr
import pyocr.builders
import pywinctl
import re
import sys
import time
import yaml

from PIL import Image
from rich.logging import RichHandler


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# Global variable for logging
logger = None


class FGO:
    OBJ = {
        'Skill': {
            'S1-1': [ 80,378],
            'S1-2': [130,378],
            'S1-3': [180,378],

            'S2-1': [257,378],
            'S2-2': [302,378],
            'S2-3': [353,378],

            'S3-1': [430,378],
            'S3-2': [480,378],
            'S3-3': [530,378],

            #Skill Target
            'ST1': [274,295],
            'ST2': [440,295],
            'ST3': [618,295],
        },
        'Attack': {
            #Attack Button
            'ATTACK': [715,379],

            #NP(Hougu) Card
            'NP1': [321,175],
            'NP2': [444,175],
            'NP3': [570,175],

            #Command Card
            'AT1': [160,331],
            'AT2': [300,331],
            'AT3': [444,331],
            'AT4': [580,331],
            'AT5': [720,331],
        },
        'Master': {
            #Master Skill
            'Skill': {
                'MS_ON': [785,243],
                'MS1': [627,243],
                'MS2': [674,243],
                'MS3': [722,243],
            },
            #'Reiju': {
            #}
            #Order Change
            'OrderChange': {
                'ODC1': [165,260],
                'ODC2': [275,260],
                'ODC3': [385,260],
                'ODC4': [490,260],
                'ODC5': [605,260],
                'ODC6': [715,260],
                'ODC_OK': [442,414],
            }
        }
    }

    RES_DIR = os.path.join(os.path.dirname(__file__), 'res')
    FRIENDS_DIR = os.path.join(os.path.dirname(__file__), 'friends')

    #Buttons
    ATTACK = os.path.join(RES_DIR, 'btn_attack.png')
    START = os.path.join(RES_DIR, 'btn_start.png')
    NEXT = os.path.join(RES_DIR, 'btn_next.png')
    CONTINUE = os.path.join(RES_DIR, 'btn_continue.png')
    CLOSE = os.path.join(RES_DIR, 'btn_close.png')
    YES = os.path.join(RES_DIR, 'btn_yes.png')
    GAPPLE = os.path.join(RES_DIR, 'icon_golden_apple.png')

    #Screen images
    IMG_SUPPORT_SCREEN = os.path.join(RES_DIR, 'img_select_support.png')
    IMG_NEED_CHARGE = os.path.join(RES_DIR, 'img_need_ap_charge.png')

    #Other fixed positions
    EMPTY = [585,414]
    FR_1ST = [404,200]
    FR_2ND = [404,335]

    REGION = None

    def __init__(self, order_sheet, iteration=1):
        self.__order_sheet = order_sheet
        self.__iteration = iteration

    def activate():
        window = pywinctl.getWindowsWithTitle('iPhoneミラーリング')[0]
        window.activate()
        window.moveTo(8, 33)
        x, y = window.topleft
        width, height = window.size
        FGO.REGION = (x, y, width, height)

    def skill(order, target=None, wait=0.1, fast=True):
        if target is None:
            logger.info(f'!!Performed Skill: \'{order}\'')
            if fast is True:
                GUI.dclick(FGO.OBJ['Skill'][order], wait)
            else:
                GUI.click(FGO.OBJ['Skill'][order], wait)
        else:
            logger.info(f'!!Performed Skill: \'{order}\' -> target: \'{target}\'')
            GUI.click(FGO.OBJ['Skill'][order])
            if fast is True:
                GUI.dclick(FGO.OBJ['Skill'][target], wait)
            else:
                GUI.click(FGO.OBJ['Skill'][target], wait)
    
    def master(order, target=None, wait=None, fast=True):
        GUI.click(FGO.OBJ['Master']['Skill']['MS_ON'])
        if target is None:
            logger.info(f'!!Master Skill: \'{order}\'')
            if fast is True:
                GUI.dclick(FGO.OBJ['Master']['Skill'][order], wait)
            else:
                GUI.click(FGO.OBJ['Master']['Skill'][order], wait)
        else:
            logger.info(f'!!Master Skill: \'{order}\' -> target: \'{target}\'')
            GUI.click(FGO.OBJ['Master']['Skill'][order])
            if fast is True:
                GUI.dclick(FGO.OBJ['Skill'][target], wait)
            else:
                GUI.click(FGO.OBJ['Skill'][target], wait)

    def order_change(targets):
        logger.info(f'!!Order Change: {targets}')
        for target in targets:
            GUI.click(FGO.OBJ['Master']['OrderChange'][target])

        GUI.dclick(FGO.OBJ['Master']['OrderChange']['ODC_OK'], 1.5)

    def attack(orders):
        logger.info(f'!!Attack: {orders}')
        GUI.click(FGO.OBJ['Attack']['ATTACK'])
        for order in orders:
            GUI.click(FGO.OBJ['Attack'][order])
        FGO.wait_for_next_wave()

    def wait_for_next_wave():
        while True:
            if GUI.find_image(FGO.ATTACK, 0.7) is not None:
                break
            if GUI.find_image(FGO.NEXT, 0.7) is not None:
                break
            GUI.click(FGO.EMPTY)

    def wait_for_support_list():
        while True:
            if GUI.find_image(FGO.IMG_SUPPORT_SCREEN, 0.7) is not None:
                break
            GUI.waits(0.5)

    def wait_for_next_button_with_tap():
        while True:
            point = GUI.find_image(FGO.NEXT, 0.7)
            if point is not None:
                GUI.click(point)
                break
            GUI.click(FGO.EMPTY)

    def shift_friend():
        GUI.drag(FGO.FR_2ND, FGO.FR_1ST, duration=0.3)

    def search_friend():
        target_pattern = r'fr_.+\.png'
        targets = [ img for img in os.listdir(FGO.FRIENDS_DIR)
                   if re.match(target_pattern, img) ]
        logger.debug(f'target friends: {targets}')

        flag = False
        for i in range(20):
            for image in targets:
                path = os.path.join(FGO.FRIENDS_DIR, image)
                point = GUI.find_image(path, 0.9)
                if point is not None:
                    flag = True
                    break
            if flag:
                break
            FGO.shift_friend()

        GUI.click(point)

    def get_current_ap():
        region = (450, 268, 90, 22)
        while True:
            current_max = OCR.read_string_by_region(region)
            if '/' in current_max:
                break
        current_ap, max_ap = current_max.split('/')

        return int(current_ap), int(max_ap)

    def get_charged_ap():
        region = (450, 260, 120, 22)
        current = OCR.read_string_by_region(region)
        remaining_ap = current.split('/')[0]

        region = (450, 281, 120, 22)
        charged = OCR.read_string_by_region(region)
        charged_ap, max_ap = charged.split('/')

        return charged_ap, remaining_ap, max_ap

    def dispatch_action(type, detail):
        if type == 'skill':
            FGO.skill(**detail)
        elif type == 'attack':
            FGO.attack(**detail)
        elif type == 'master':
            FGO.master(**detail)
        elif type == 'order_change':
            FGO.order_change(**detail)

    def get_order(self):
        with open(self.__order_sheet) as file:
            self.__orders = yaml.load(file, yaml.Loader)
            return self.__orders

    def start_quest(self):
        logger.info("=== Start Quest ===")
        FGO.search_friend()
        GUI.click_image(FGO.START)
        FGO.wait_for_next_wave()

    def select_friend(self):
        logger.info("=== Select a support ===")
        FGO.search_friend()
        FGO.wait_for_next_wave()

    def process_quest(self):
        for wave in self.__orders:
            for name, actions in wave.items():
                logger.info(f"=== {name} ===")
                for action in actions:
                    for type, detail in action.items():
                        logger.debug(f'{type} -> {detail}')
                        FGO.dispatch_action(type, detail)
    
    def pass_result(self):
        logger.info("=== RESULT ===")
        FGO.wait_for_next_button_with_tap()
        current_ap, max_ap = FGO.get_current_ap()
        logger.info(f'@@@ Remaining AP: {current_ap}/{max_ap}')

    def continue_battle():
        GUI.click_image(FGO.CONTINUE)

    def cancel_battle():
        GUI.click_image(FGO.CLOSE)

    def is_need_charge():
        if GUI.find_image(FGO.IMG_NEED_CHARGE, 0.7) is not None:
            logger.info(f'@@@ AP Charge NEEDED')
            return True
        else:
            return False

    def charge_apple():
        logger.info("=== AP CHARGE ===")
        elapsed = Elapse()
        elapsed.start()
        GUI.click_image(FGO.GAPPLE)
        charged_ap, remaining_ap, max_ap = FGO.get_charged_ap()
        GUI.click_image(FGO.YES)
        elapsed.end()

        logger.info(f'@@@ AP Charge Time: {elapsed.strfmt()}.')
        logger.info(f'@@@ Charged {charged_ap}({remaining_ap}+{max_ap})/{max_ap}')

    def run(self):
        logger.info('=== FGO AUTO STARTED ===')
        logger.info(f'@@@ Order Sheet: {self.__order_sheet}')
        logger.info(f'@@@ Iteration: {self.__iteration}')

        self.get_order()
        FGO.activate()

        max_loop = self.__iteration
        logger.info(f'@@@ Quest Loop Started 0/{max_loop}')

        for i in range(max_loop):
            FGO.wait_for_support_list()
            if i < 1:
                self.start_quest()
            else:
                self.select_friend()

            quest_elapsed = Elapse()
            quest_elapsed.start()
            self.process_quest()
            self.pass_result()
            quest_elapsed.end()

            logger.info(f'@@@ Quest Clear Time: {quest_elapsed.strfmt()}.')
            logger.info(f'@@@ Quest Cleared {i + 1}/{max_loop}')

            if i < max_loop - 1:
                FGO.continue_battle()
                if FGO.is_need_charge():
                    FGO.charge_apple()
            else:
                FGO.cancel_battle()


class GUI:
    def waits(sec):
        logger.debug(f"Wait {sec} seconds")
        time.sleep(sec)

    def drag(point_from, point_to, duration=0.5):
        pyautogui.moveTo(point_from)
        pyautogui.dragTo(point_to, duration=duration, button='left')

    def click(point, wait=None):
        logger.debug(f"Click at {point}")
        pyautogui.click(point)
        if wait is not None:
            GUI.waits(wait)

    def dclick(point, wait=None):
        logger.debug(f"DoubleClick at {point}")
        pyautogui.click(point, clicks=2, interval=0.5)
        if wait is not None:
            GUI.waits(wait)

    def tclick(point, wait=None):
        logger.debug(f"TripleClick at {point}")
        pyautogui.click(point, clicks=3, interval=0.5)
        if wait is not None:
            GUI.waits(wait)

    def find_image(image_path, confidence):
        logger.debug(image_path)
        try:
            point = pyautogui.locateCenterOnScreen(image_path, confidence=confidence, grayscale=True, region=FGO.REGION)
        except pyautogui.ImageNotFoundException:
            return None
        else:
            return point

    def click_image(image, timeout=2):
        elapsed = Elapse()
        elapsed.start()
        while elapsed.end() < timeout:
            point = GUI.find_image(image, 0.7)
            if point is not None:
                GUI.click(point)
                break


class OCR:
    def pil2cv(pil_image):
        cv_image = np.array(pil_image, dtype=np.uint8)
        if cv_image.ndim == 2: # mono
            pass
        elif cv_image.shape[2] == 3: # color
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
        elif cv_image.shape[2] == 4: # transparent
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGBA2BGRA)
        return cv_image

    def cv2pil(cv_image):
        pil_image = cv_image.copy()
        if pil_image.ndim == 2: # mono
            pass
        elif pil_image.shape[2] == 3: # color
            pil_image = cv2.cvtColor(pil_image, cv2.COLOR_BGR2RGB)
        elif pil_image.shape[2] == 4: # transparent
            pil_image = cv2.cvtColor(pil_image, cv2.COLOR_BGRA2RGBA)
        return pil_image

    def preproc_image(image, grayscale=True, denoise=True, binarize=False, bitwise=False):
        # Convert PIL image to CV2 image
        img = OCR.pil2cv(image)

        # Transform resolution to 300dpi
        height, width = img.shape[:2]
        new_height = int(height * (300 / 72)) # 72dpi to 300dpi
        new_width = int(width * (300 / 72))
        img = cv2.resize(img, (new_width, new_height))

        # Gray scale
        if grayscale:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #cv2.imwrite("debug_gray.png", img)
        # Denoise
        if denoise:
            img = cv2.bilateralFilter(img, 9, 75, 75)
            #cv2.imwrite("debug_denoise.png", img)
        # Binary
        if binarize:
            _, img = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            #cv2.imwrite("debug_binary.png", img)
        # Bitwise
        if bitwise:
            img = cv2.bitwise_not(img)
            #cv2.imwrite('debug_bitwise.png', img)
        
        new_img = img.copy()
        new_img = Image.fromarray(new_img)
        return new_img

    def ocr_numeric(target):
        tools = pyocr.get_available_tools()
        tool = tools[0]

        builder = pyocr.builders.TextBuilder(tesseract_layout=7)
        builder.tesseract_configs.append('-c')
        builder.tesseract_configs.append('tessedit_char_whitelist="0123456789/"')

        str = tool.image_to_string(target, lang='jpn+eng', builder=builder)
        return str

    def read_string_by_region(region):
        img = pyautogui.screenshot(region=region)

        target_image = OCR.preproc_image(img)
        str = OCR.ocr_numeric(target_image)
        logger.debug(str)
        return str


class Elapse:
    def __init__(self):
        self.__start = time.time()
        self.__end = time.time()

    def start(self):
        self.__start = time.time()

    def reset(self):
        self.__start = time.time()

    def end(self):
        self.__end = time.time() 
        return self.__end - self.__start

    def strfmt(self):
        self.__elapsed = self.__end - self.__start 
        return '{:.2f} seconds'.format(self.__elapsed)


def set_logger(debug):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format='%(message)s',
        datefmt='[%X]',
        handlers=[ RichHandler(markup=True, rich_tracebacks=True) ]
    )

    global logger
    logger = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser(
        description='FGO AUTO: an automation script for FGO quest iteration'
    )
    parser.add_argument('order_sheet', help='a file of FGO Auto order sheet')
    parser.add_argument('-i', '--iteration', help='Number of loop for the target quest', type=int, default=1)
    parser.add_argument('--debug', help='DEBUG mode for development', action='store_true')

    return parser.parse_args()


def main():
    args = get_args()
    set_logger(args.debug)

    FGO(args.order_sheet, args.iteration).run()


if __name__ == '__main__':
    main()
