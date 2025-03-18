import flet as ft
import sympy as sp
from datetime import datetime
import json

class CalcButton(ft.ElevatedButton):
    def __init__(self, text, on_click, expand=1):
        super().__init__(text=text, on_click=on_click)
        self.expand = expand
        self.data = text

class DigitButton(CalcButton):
    def __init__(self, text, on_click, expand=1):
        super().__init__(text, on_click, expand)
        self.bgcolor = ft.colors.WHITE24
        self.color = ft.colors.WHITE

class ActionButton(CalcButton):
    def __init__(self, text, on_click):
        super().__init__(text, on_click)
        self.bgcolor = ft.colors.ORANGE
        self.color = ft.colors.WHITE

class ExtraActionButton(CalcButton):
    def __init__(self, text, on_click):
        super().__init__(text, on_click)
        self.bgcolor = ft.colors.BLUE_GREY_100
        self.color = ft.colors.BLACK

class CalculatorApp(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expression = ft.Text(value="", color=ft.colors.GREY_400, size=18)
        self.result = ft.Text(value="0", color=ft.colors.WHITE, size=20)
        self.width = 350
        self.bgcolor = ft.colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.current_operand_start = 0
        self.show_history = False
        self.history = []

        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.expression], alignment="end"),
                ft.Row(controls=[self.result], alignment="end"),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="History", on_click=self.toggle_history),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="CE", on_click=self.button_clicked),
                        ExtraActionButton(text="⬅️", on_click=self.button_clicked),
                        ExtraActionButton(text="(", on_click=self.button_clicked),
                        ExtraActionButton(text=")", on_click=self.button_clicked),
                        ActionButton(text="/", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", on_click=self.button_clicked),
                        DigitButton(text="8", on_click=self.button_clicked),
                        DigitButton(text="9", on_click=self.button_clicked),
                        ActionButton(text="*", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", on_click=self.button_clicked),
                        DigitButton(text="5", on_click=self.button_clicked),
                        DigitButton(text="6", on_click=self.button_clicked),
                        ActionButton(text="-", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", on_click=self.button_clicked),
                        DigitButton(text="2", on_click=self.button_clicked),
                        DigitButton(text="3", on_click=self.button_clicked),
                        ActionButton(text="+", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, on_click=self.button_clicked),
                        DigitButton(text=".", on_click=self.button_clicked),
                        ActionButton(text="=", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ActionButton(text="√", on_click=self.button_clicked),
                        ActionButton(text="^", on_click=self.button_clicked),
                        ActionButton(text="sin", on_click=self.button_clicked),
                        ActionButton(text="cos", on_click=self.button_clicked),
                    ]
                ),
                self.build_history_panel()
            ]
        )

    def did_mount(self):
        self.load_history()
        self.update_history_panel()

    def load_history(self):
        history_data = self.page.client_storage.get('history')
        if history_data:
            try:
                self.history = json.loads(history_data)
            except json.JSONDecodeError:
                self.history = []

    def save_history(self):
        history_data = json.dumps(self.history)
        self.page.client_storage.set('history', history_data)

    def toggle_history(self, e):
        self.show_history = not self.show_history
        self.history_panel.visible = self.show_history
        self.update()

    def build_history_panel(self):
        self.history_panel = ft.Container(
            content=ft.Column(
                controls=[],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=300,
            height=200,
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            visible=False,
        )
        return self.history_panel

    def button_clicked(self, e):
        data = e.control.data
        if data in ("AC", "CE"):
            if data == "CE":
                self.expression.value = self.expression.value[:self.current_operand_start]
            else:
                self.expression.value = ""
            self.result.value = "0"
        elif data == "⬅️":
            if self.expression.value:
                self.expression.value = self.expression.value[:-1]
        elif data in ("(", ")", "^", "√", "sin", "cos"):
            if data == "√":
                self.expression.value += "sqrt("
            elif data in ("sin", "cos"):
                self.expression.value += f"{data}("
            else:
                self.expression.value += data
        elif data == "=":
            try:
                expr = self.expression.value
                if expr:
                    result = float(sp.sympify(expr).evalf())
                    formatted_result = self.format_number(result)
                    self.result.value = formatted_result
                    if expr and not self.expression.value.endswith(data):
                        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_entry = {
                            "index": len(self.history) + 1,
                            "datetime": datetime_str,
                            "expression": expr,
                            "result": formatted_result,
                        }
                        if len(self.history) >= 10:
                            self.history.pop(0)
                        self.history.append(new_entry)
                        self.save_history()
                        self.update_history_panel()
                else:
                    self.result.value = "0"
            except:
                self.result.value = "Error"
            self.expression.value = ""
        else:
            if data in ("+", "-", "*", "/", "^", "(", ")", "√", "sin", "cos"):
                if self.expression.value and self.expression.value[-1] in ("+", "-", "*", "/", "^", "(", "√", "sin", "cos"):
                    if data == "-":
                        self.expression.value += data
                    else:
                        return
            self.expression.value += data
            try:
                preview = float(sp.sympify(self.expression.value).evalf())
                formatted_preview = self.format_number(preview)
                self.result.value = formatted_preview
            except:
                self.result.value = self.expression.value

        self.current_operand_start = len(self.expression.value)
        self.update()

    def update_history_panel(self):
        history_controls = []
        for idx, entry in enumerate(reversed(self.history)):
            entry_row_index = len(self.history) - 1 - idx
            entry_row = ft.Row(
                controls=[
                    ft.Text(str(entry["index"]), size=12, color=ft.colors.WHITE),
                    ft.Text(entry["datetime"], size=12, color=ft.colors.WHITE),
                    ft.Text(entry["expression"], size=12, color=ft.colors.WHITE),
                    ft.Text(entry["result"], size=12, color=ft.colors.WHITE),
                    ft.IconButton(
                        ft.icons.DELETE,
                        on_click=lambda e, i=entry_row_index: self.delete_history_entry(i),
                        icon_color=ft.colors.RED,
                    ),
                    ft.IconButton(
                        ft.icons.CONTENT_COPY,
                        on_click=lambda e, res=entry["result"]: self.copy_to_clipboard(res),
                        icon_color=ft.colors.BLUE,
                    ),
                ],
                spacing=10,
            )
            history_controls.append(entry_row)
        self.history_panel.content.controls = history_controls
        self.update()

    def delete_history_entry(self, index):
        if 0 <= index < len(self.history):
            del self.history[index]
            self.save_history()
            self.update_history_panel()

    def copy_to_clipboard(self, result):
        ft.clipboard.set(result)

    def format_number(self, num):
        if isinstance(num, float):
            if num.is_integer():
                return f"{int(num):,}".replace(",", " ")
            else:
                parts = str(num).split('.')
                integer_part = parts[0].replace(',', ' ')
                decimal_part = parts[1].rstrip('0').rstrip('.')
                return f"{integer_part}.{decimal_part}" if decimal_part else integer_part
        return str(num).replace(',', ' ')

def main(page: ft.Page):
    page.title = "Calc App"
    calc = CalculatorApp(page)
    page.add(calc)
    calc.did_mount()  

ft.app(target=main)