import os
import re
from datetime import datetime

import openai


class ChatGPT:
    SELECT_MAX_RETRY = 5
    ANSWER_MAX_RETRY = 3

    def __init__(self, api_key, work_preserve):
        openai.api_key = api_key
        os.makedirs("tmp/log", exist_ok=True)
        self.log_path = os.path.join(
            "tmp", "log", f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        )
        self.work_preserve = work_preserve
        self.prompt_select = self.load_prompt("template_select.txt")
        self.prompt_answer = self.load_prompt("template_answer.txt")
        self.prompt_judge = self.load_prompt("template_judge.txt")
        self.work, self.keyword = self.select_keyword()

    def logging(self, text):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(str(text) + "\n")

    def load_prompt(self, filename):
        with open(f"lib/prompt/{filename}", "r", encoding="utf-8") as f:
            text = f.read()
        return text

    def select_keyword(self):
        text = self.prompt_select.format(work_preserve=self.work_preserve)
        keywords = []
        for _ in range(ChatGPT.SELECT_MAX_RETRY):
            res = self.request_to_chatgpt(text)
            work = res.strip().split("\n")[0]
            keyword = res.strip().split("\n")[-1]
            keywords.append(keyword)
            if "代表作: " in work and "キャラクター名: " in keyword:
                work = re.sub("代表作: ", "", work)
                keyword = re.sub("キャラクター名: ", "", keyword)
                return work, keyword
        raise Exception(f"キーワードの選択に失敗しました: {keywords}")

    def ask_answer(self, question):
        self.logging("----------")
        self.logging("question: " + question)

        text = self.prompt_answer.format(
            work=self.work, keyword=self.keyword, question=question
        )

        for _ in range(ChatGPT.ANSWER_MAX_RETRY):
            res = self.request_to_chatgpt(text)
            keyword = res.strip().split("\n")[-1]
            if "返答: " in keyword:
                answer = re.sub("返答: ", "", keyword)
                break
        else:
            answer = "分からない"

        self.logging("answer: " + answer)

        return answer

    def judge(self, question):
        self.logging("----------")
        self.logging("question: " + question)
        text = self.prompt_judge.format(
            work=self.work, keyword1=self.keyword, keyword2=question
        )

        res = self.request_to_chatgpt(text)
        answer = res.strip().split("\n")[-1]
        if "同じものである" in answer:
            judge = "正解！"
        else:
            judge = "残念！"
        answer = "\n".join(
            [
                judge,
                "私が考えていたのは",
                self.keyword,
                "でした！",
            ]
        )

        self.logging(answer)

        return answer

    def request_to_chatgpt(self, content):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
        )
        res = completion.choices[0].message.content
        self.logging(res)
        return res
