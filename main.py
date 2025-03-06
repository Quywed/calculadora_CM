import flet as ft
from sympy import sympify, SympifyError, sqrt, log, Pow
from datetime import datetime
import json

# Define the base button class
class CalcButton(ft.ElevatedButton):
    def __init__(self, text, expand=1, on_click=None, **kwargs):
        super().__init__(text=text, expand=expand, on_click=on_click, **kwargs)


# Define child classes for different types of buttons
class DigitButton(CalcButton):
    def __init__(self, text, expand=1, on_click=None):
        super().__init__(text=text, expand=expand, on_click=on_click)
        self.bgcolor = ft.colors.WHITE24
        self.color = ft.colors.WHITE


class ActionButton(CalcButton):
    def __init__(self, text, expand=1, on_click=None):
        super().__init__(text=text, expand=expand, on_click=on_click)
        self.bgcolor = ft.colors.ORANGE
        self.color = ft.colors.WHITE


class ExtraActionButton(CalcButton):
    def __init__(self, text, expand=1, on_click=None):
        super().__init__(text=text, expand=expand, on_click=on_click)
        self.bgcolor = ft.colors.BLUE_GREY_100
        self.color = ft.colors.BLACK


def main(page: ft.Page):
    page.title = "Advanced Calculator"

    # Text to display the expression and result
    expression = ft.Text(value="", size=20, color=ft.colors.GREY_400, text_align=ft.TextAlign.RIGHT)
    result = ft.Text(value="0", size=30, color=ft.colors.WHITE, text_align=ft.TextAlign.RIGHT)

    # Load history from local storage
    def load_history():
        stored_history = page.client_storage.get("calculator.history")
        return json.loads(stored_history) if stored_history else []

    # Save history to local storage
    def save_history():
        page.client_storage.set("calculator.history", json.dumps(history))

    # History list
    history = load_history()
    history_visible = False

    # Function to handle button clicks
    def button_click(e):
        nonlocal history, history_visible

        if e.control.text == "AC":
            expression.value = ""
            result.value = "0"
        elif e.control.text == "CE":
            expression.value = expression.value[:-1]
            if not expression.value:
                result.value = "0"
        elif e.control.text == "⬅️":
            expression.value = expression.value[:-1]
        elif e.control.text == "=":
            try:
                # Replace commas with dots for decimal numbers
                expr_str = expression.value.replace(",", ".")

                # Evaluate the expression using SymPy
                expr = sympify(expr_str)
                calculated_result = "{:,.0f}".format(expr.evalf()) if expr.is_integer else "{:,.6f}".format(expr.evalf())

                # Add to history if it's a new calculation
                if expression.value and result.value != "0":
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    history.insert(0, {
                        "index": len(history) + 1,
                        "timestamp": timestamp,
                        "expression": expression.value,
                        "result": calculated_result
                    })

                    # Limit history to 10 entries
                    if len(history) > 10:
                        history.pop()

                    # Save history to local storage
                    save_history()

                result.value = calculated_result
                expression.value = ""  # Clear expression after calculation
            except SympifyError:
                result.value = "Error: Invalid Expression"
            except Exception as ex:
                result.value = f"Error: {str(ex)}"
        elif e.control.text in "0123456789.()*/+-":
            # Append the clicked button's text to the expression
            expression.value += e.control.text
            result.value = ""  # Clear result when building a new expression
        elif e.control.text == "√":
            if expression.value:
                try:
                    expr = sympify(expression.value.replace(",", "."))
                    result.value = "{:,.6f}".format(sqrt(expr).evalf())
                except Exception:
                    result.value = "Error: Invalid Input for √"
        elif e.control.text == "1/x":
            if expression.value:
                try:
                    expr = sympify(expression.value.replace(",", "."))
                    if expr == 0:
                        result.value = "Error: Division by Zero"
                    else:
                        result.value = "{:,.6f}".format((1 / expr).evalf())
                except Exception:
                    result.value = "Error: Invalid Input for 1/x"
        elif e.control.text == "x²":
            if expression.value:
                try:
                    expr = sympify(expression.value.replace(",", "."))
                    result.value = "{:,.0f}".format(Pow(expr, 2).evalf()) if Pow(expr, 2).is_integer else "{:,.6f}".format(Pow(expr, 2).evalf())
                except Exception:
                    result.value = "Error: Invalid Input for x²"
        elif e.control.text == "log":
            if expression.value:
                try:
                    expr = sympify(expression.value.replace(",", "."))
                    if expr <= 0:
                        result.value = "Error: Logarithm of Non-positive Number"
                    else:
                        result.value = "{:,.6f}".format(log(expr).evalf())
                except Exception:
                    result.value = "Error: Invalid Input for log"
        elif e.control.text == "History":
            history_visible = not history_visible
            history_list.visible = history_visible  # Toggle visibility
            update_history_display()  # Ensure history is updated

        page.update()

    # Function to create a history item
    def create_history_item(item):
        index = item["index"]
        timestamp = item["timestamp"]
        expression_value = item["expression"]
        result_value = item["result"]

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(f"{index}", width=30, text_align=ft.TextAlign.RIGHT),
                    ft.Text(f"{timestamp}", width=150, text_align=ft.TextAlign.LEFT),
                    ft.Text(f"{expression_value} = {result_value}", width=200, text_align=ft.TextAlign.LEFT),
                    ft.ElevatedButton("Delete", on_click=lambda e, i=index - 1: delete_history_item(i)),
                    ft.ElevatedButton("Copy", on_click=lambda e, r=result_value: copy_to_clipboard(r))
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=5,
            bgcolor=ft.colors.GREY_800,
            border_radius=5
        )

    # Function to delete a history item
    def delete_history_item(index):
        nonlocal history
        if 0 <= index < len(history):
            del history[index]
            save_history()  # Save updated history
            update_history_display()

    # Function to copy result to clipboard
    def copy_to_clipboard(result_value):
        page.set_clipboard(result_value)
        page.show_snack_bar(ft.SnackBar(ft.Text(f"Copied {result_value} to clipboard!"), open=True))

    # Function to update history display
    def update_history_display():
        history_list.controls = [create_history_item(item) for item in history]
        page.update()

    # Create history list view
    history_list = ft.Column(scroll="auto", visible=False, height=200)

    # Define the calculator layout inside a container
    page.add(
        ft.Container(
            width=400,
            bgcolor=ft.colors.BLACK,
            border_radius=ft.border_radius.all(20),
            padding=20,
            content=ft.Column(
                controls=[
                    # Row for the expression display
                    ft.Row(
                        controls=[expression],
                        alignment=ft.MainAxisAlignment.END
                    ),
                    # Row for the result display
                    ft.Row(
                        controls=[result],
                        alignment=ft.MainAxisAlignment.END
                    ),
                    # Row for extra action buttons
                    ft.Row(
                        controls=[
                            ExtraActionButton(text="AC", on_click=button_click, expand=1),
                            ExtraActionButton(text="CE", on_click=button_click, expand=1),
                            ExtraActionButton(text="⬅️", on_click=button_click, expand=1),
                            ActionButton(text=")", on_click=button_click, expand=1),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    # Row for advanced functions
                    ft.Row(
                        controls=[
                            ActionButton(text="√", on_click=button_click, expand=1),
                            ActionButton(text="1/x", on_click=button_click, expand=1),
                            ActionButton(text="x²", on_click=button_click, expand=1),
                            ActionButton(text="log", on_click=button_click, expand=1),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    # Row for the first set of buttons (extra action buttons)
                    ft.Row(
                        controls=[
                            ExtraActionButton(text="(", on_click=button_click, expand=1),
                            DigitButton(text="7", on_click=button_click, expand=1),
                            DigitButton(text="8", on_click=button_click, expand=1),
                            DigitButton(text="9", on_click=button_click, expand=1),
                            ActionButton(text="/", on_click=button_click, expand=1),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    # Row for the second set of buttons (digits and multiplication)
                    ft.Row(
                        controls=[
                            DigitButton(text="4", on_click=button_click, expand=1),
                            DigitButton(text="5", on_click=button_click, expand=1),
                            DigitButton(text="6", on_click=button_click, expand=1),
                            ActionButton(text="*", on_click=button_click, expand=1),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    # Row for the third set of buttons (digits and subtraction)
                    ft.Row(
                        controls=[
                            DigitButton(text="1", on_click=button_click, expand=1),
                            DigitButton(text="2", on_click=button_click, expand=1),
                            DigitButton(text="3", on_click=button_click, expand=1),
                            ActionButton(text="-", on_click=button_click, expand=1),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    # Row for the fourth set of buttons (digits and addition)
                    ft.Row(
                        controls=[
                            DigitButton(text="0", expand=2, on_click=button_click),
                            DigitButton(text=".", on_click=button_click, expand=1),
                            ActionButton(text="+", on_click=button_click, expand=1),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    # Row for equals and history button
                    ft.Row(
                        controls=[
                            ActionButton(text="=", on_click=button_click, expand=2),
                            ExtraActionButton(text="History", on_click=button_click, expand=2),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    # History display
                    history_list,
                ],
                spacing=10  # Add spacing between rows
            )
        )
    )

    # Initial history display update
    update_history_display()


ft.app(main)