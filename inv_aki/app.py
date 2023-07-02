import argparse

import pygame
from pygame.locals import MOUSEBUTTONDOWN, QUIT

from inv_aki.chatgpt import ChatGPT
from inv_aki.text_box import TextBox


class MainFrame:
    BLACK = (0, 0, 0)
    WINDOW_SIZE = (1790, 1276)
    BACKGOUND_PATH = "lib/images/background.jpg"
    PLAYER_PATH = "lib/images/player.png"
    CHATGPT_PATH = "lib/images/chatgpt.png"
    BUBBLE_PATH = "lib/images/bubble.png"

    SCENE_INIT = 0
    SCENE_MAIN_START = 1
    SCENE_MAIN = 2
    SCENE_MAIN_ANSWER = 3
    SCENE_END = 9

    MAX_QUESTION_COUNT = 20

    def __init__(self, work=None):
        pygame.init()

        # ChatGPT
        self.chatgpt = None

        # アセット部分
        self.screen = pygame.display.set_mode(MainFrame.WINDOW_SIZE)
        self.background = self.load_background()
        self.player_illust = self.load_player_illust()
        self.chatgpt_illust = self.load_chatgpt_illust()
        self.bubble = self.load_bubble()
        self.button1 = pygame.Rect(800, 500, 200, 50)
        self.button2 = pygame.Rect(1100, 500, 200, 50)
        self.font = pygame.font.SysFont("meiryo", 32)

        # パラメータ部分
        self.scene = MainFrame.SCENE_INIT
        self.api_key = ""
        self.question = ""
        self.chatgpt_illust_answer = ""
        self.question_count = 0

        # workを指定して実行された場合，
        # キャラクター選択のプロンプトに追記する
        self.work_preserve = self.create_work_preserve(work)

    def create_work_preserve(self, work=None):
        if work is not None:
            return f"挙げる際は，{work} を代表作として挙げてください．"
        else:
            return ""

    def set_scene(self, scene):
        self.question = ""
        self.chatgpt_illust_answer = ""
        if scene == MainFrame.SCENE_MAIN_START:
            self.chatgpt = ChatGPT(self.api_key, self.work_preserve)
            self.question_count = 0
        self.scene = scene

    def load_background(self):
        background = pygame.image.load(MainFrame.BACKGOUND_PATH)
        background = pygame.transform.scale(background, MainFrame.WINDOW_SIZE)
        return background

    def load_player_illust(self):
        player_illust = pygame.image.load(MainFrame.PLAYER_PATH)
        return player_illust

    def load_chatgpt_illust(self):
        chatgpt_illust = pygame.image.load(MainFrame.CHATGPT_PATH)
        chatgpt_illust = pygame.transform.scale(chatgpt_illust, (300, 510))
        return chatgpt_illust

    def load_bubble(self):
        bubble = pygame.image.load(MainFrame.BUBBLE_PATH)
        return bubble

    def parse_text(self, text):
        texts = []
        t = text
        while t:
            texts.append(t[:20])
            t = t[20:]
        return "\n".join(texts)

    def _render_text(self, text_line, x, y):
        t = self.font.render(text_line, True, MainFrame.BLACK)
        self.screen.blit(t, (x, y))

    def render_player_text(self, texts):
        for i, text_line in enumerate(texts):
            self._render_text(text_line, 800, 300 + 30 * i)

    def render_chatgpt_text(self, texts):
        for i, text_line in enumerate(texts):
            self._render_text(text_line, 700, 900 + 30 * i)

    def render_question_count(self):
        text = f"質問回数: {self.question_count} / {MainFrame.MAX_QUESTION_COUNT}"
        self._render_text(text, 800, 420)

    def render_button_1(self, text):
        pygame.draw.rect(self.screen, (200, 200, 200), self.button1)
        self._render_text(text, 800, 500)

    def render_button_2(self, text):
        pygame.draw.rect(self.screen, (200, 200, 200), self.button2)
        self._render_text(text, 1100, 500)

    def render_background(self):
        self.screen.fill(MainFrame.BLACK)
        self.screen.blit(self.background, (0, 0))

    def render_main_base(self):
        if self.scene >= MainFrame.SCENE_MAIN_START:
            self.screen.blit(self.player_illust, (20, 0))
            self.screen.blit(self.chatgpt_illust, (1400, 600))
            self.screen.blit(pygame.transform.rotate(self.bubble, 180), (600, 100))
            self.screen.blit(self.bubble, (500, 700))

    def render_main_start(self):
        if self.scene == MainFrame.SCENE_MAIN_START:
            self.render_player_text(
                [
                    "やぁ，私はアキネイターです",
                    "有名な人物やキャラクターを思い浮かべて．",
                    "魔人が誰でも当てて見せよう．",
                    "魔人は何でもお見通しさ．",
                ]
            )

            self.render_chatgpt_text(
                [
                    "よーし，やってみるぞー",
                ]
            )
            self.render_button_1("スタート")
            self.render_button_2("終了")

    def render_main(self):
        if self.scene == MainFrame.SCENE_MAIN:
            if self.question == "":
                self.question = TextBox.popup("質問文を入力してください")
                self.chatgpt_answer = self.chatgpt.ask_answer(self.question)
                self.question_count += 1

            self.render_player_text(self.parse_text(self.question).split("\n"))

            self.render_chatgpt_text(self.chatgpt_answer.split("\n"))
            self.render_question_count()
            if self.question_count < MainFrame.MAX_QUESTION_COUNT:
                self.render_button_1("次の質問")
            self.render_button_2("お題を当てる")

    def render_main_answer(self):
        if self.scene == MainFrame.SCENE_MAIN_ANSWER:
            if self.question == "":
                self.question = TextBox.popup("ChatGPTが何について回答しているか入力してください")
                self.chatgpt_answer = self.chatgpt.judge(self.question)

            self.render_player_text(self.parse_text(self.question).split("\n"))

            self.render_chatgpt_text(self.chatgpt_answer.split("\n"))
            self.render_question_count()
            self.render_button_1("最初に戻る")
            self.render_button_2("終了")

    def is_quit(self, events):
        return any(event.type == QUIT for event in events)

    def check_finish(self, events):
        if self.is_quit(events):
            pygame.quit()
            self.set_scene(MainFrame.SCENE_END)

    def check_api_key(self, events):
        if self.scene == MainFrame.SCENE_INIT:
            self.api_key = TextBox.popup("ChatGPT の APIkey を入力してください")
            self.set_scene(MainFrame.SCENE_MAIN_START)

    def check_button(self, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if self.button1.collidepoint(event.pos):
                    self.press_button_1()
                if self.button2.collidepoint(event.pos):
                    self.press_button_2()

    def press_button_1(self):
        if self.scene == MainFrame.SCENE_MAIN_START:
            # スタートボタンなので，MAINに移行する
            self.set_scene(MainFrame.SCENE_MAIN)
        elif self.scene == MainFrame.SCENE_MAIN:
            # 次の質問なので，質問回数が残っていればMAINをやり直す
            if self.question_count < MainFrame.MAX_QUESTION_COUNT:
                self.set_scene(MainFrame.SCENE_MAIN)
        elif self.scene == MainFrame.SCENE_MAIN_ANSWER:
            # 最初に戻るなので，MAIN_START に戻る
            self.set_scene(MainFrame.SCENE_MAIN_START)

    def press_button_2(self):
        if self.scene == MainFrame.SCENE_MAIN_START:
            # 終了ボタンなので，終了する
            self.set_scene(MainFrame.SCENE_END)
        elif self.scene == MainFrame.SCENE_MAIN:
            # お題を当てるボタンなので，MAIN_ANSWERに移行する
            self.set_scene(MainFrame.SCENE_MAIN_ANSWER)
        elif self.scene == MainFrame.SCENE_MAIN_ANSWER:
            # 終了ボタンなので，終了する
            self.set_scene(MainFrame.SCENE_END)

    def run(self):
        while self.scene != MainFrame.SCENE_END:
            self.render_background()
            self.render_main_base()
            self.render_main_start()
            self.render_main()
            self.render_main_answer()
            pygame.display.update()
            events = pygame.event.get()
            self.check_finish(events)
            self.check_button(events)
            self.check_api_key(events)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work")
    return parser.parse_args()


def main():
    args = get_args()
    main_frame = MainFrame(work=args.work)
    main_frame.run()


if __name__ == "__main__":
    main()
