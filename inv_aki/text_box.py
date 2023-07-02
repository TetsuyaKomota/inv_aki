import tkinter


class TextBox:
    @classmethod
    def popup(self, description):
        root = tkinter.Tk()
        root.geometry("900x200")
        root.title(description)

        txt = tkinter.Entry(width=50, font=("", 24))
        txt.place(x=50, y=70)

        output = ""

        def close():
            nonlocal output
            output = txt.get()
            root.destroy()

        # ボタン作成
        btn = tkinter.Button(root, text="決定", command=close, font=("", 20))
        btn.place(x=400, y=120)

        # 表示
        root.mainloop()

        return output


if __name__ == "__main__":
    text = TextBox.popup("入力してください")
    print(text)
