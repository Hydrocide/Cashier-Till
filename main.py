import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import os

TAX_RATE = 0.13
item_dict = {}

def button_clicked(button_number):
    selected_item = f"Item {button_number}"
    selected_cost = 10 * button_number
    add_item(selected_item, selected_cost)

def search():
    searched_code = search_entry.get()
    if searched_code in item_dict:
        selected_item = searched_code
        selected_cost = item_dict[searched_code]
        add_item(selected_item, selected_cost)
    else:
        messagebox.showerror("Item Not Found", "Item code not found")

def add_item(item, cost):
    for child in tree.get_children():
        if tree.item(child, "values")[1] == item:
            quantity = int(tree.item(child, "values")[2]) + 1
            total_cost = cost * quantity
            tree.item(child, values=(tree.item(child, "values")[0], item, quantity, cost, total_cost))
            calculate_order_totals()
            return
    line_num = len(tree.get_children()) + 1
    tree.insert("", "end", values=(line_num, item, 1, cost, cost))
    item_dict[line_num] = cost
    calculate_order_totals()

def remove_item():
    selected_line = int(line_number_entry.get())
    for child in tree.get_children():
        line_num = int(tree.item(child, "values")[0])
        if line_num == selected_line:
            tree.delete(child)
            del item_dict[line_num]
    calculate_order_totals()

def calculate_order_totals():
    subtotal = 0
    for child in tree.get_children():
        subtotal += float(tree.item(child, "values")[4])
    tax = subtotal * TAX_RATE
    total = subtotal + tax
    subtotal_label.config(text=f"Order Subtotal: ${subtotal:.2f}")
    total_label.config(text=f"Order Total (incl. 13% tax): ${total:.2f}")

def load_items_from_file(filename):
    items_list = []
    with open(filename, "r") as file:
        for line in file:
            item_code, item_name, item_cost = line.strip().split(", ")
            items_list.append((item_code, item_name, item_cost))
            if len(items_list) == 4:
                break

    for i, (item_code, item_name, item_cost) in enumerate(items_list):
        button_text = f"{item_name}\n${item_cost}"
        button_func = lambda code=item_code, cost=float(item_cost): add_item(code, cost)
        buttons[i].config(text=button_text, command=button_func)



root = tk.Tk()
root.title("Resizable Tkinter App")

# Create parent frame
parent_frame = tk.Frame(root)
parent_frame.grid(row=0, column=0, sticky="nsew")

# Rest of your GUI setup code...



# Create frame for buttons
buttons_frame = tk.Frame(parent_frame)
buttons_frame.grid(row=0, column=0, sticky="nsew")

button1 = tk.Button(buttons_frame, text="Button 1", command=lambda: button_clicked(1))
button1.grid(row=0, column=0, sticky="nsew")

button2 = tk.Button(buttons_frame, text="Button 2", command=lambda: button_clicked(2))
button2.grid(row=0, column=1, sticky="nsew")

button3 = tk.Button(buttons_frame, text="Button 3", command=lambda: button_clicked(3))
button3.grid(row=1, column=0, sticky="nsew")

button4 = tk.Button(buttons_frame, text="Button 4", command=lambda: button_clicked(4))
button4.grid(row=1, column=1, sticky="nsew")

# Create frame for search bar
search_frame = tk.Frame(buttons_frame)
search_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")

search_button = tk.Button(search_frame, text="Search", command=search)
search_button.grid(row=0, column=0, sticky="nsew")

search_entry = tk.Entry(search_frame, width=5)
search_entry.grid(row=0, column=1, sticky="nsew")

# Create frame for remove bar
remove_frame = tk.Frame(buttons_frame)
remove_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")

remove_button = tk.Button(remove_frame, text="Remove Item", command=remove_item)
remove_button.grid(row=0, column=0, sticky="nsew")

line_number_entry = tk.Entry(remove_frame, width=5)
line_number_entry.grid(row=0, column=1, sticky="nsew")

# Create frame for treeview
tree_frame = tk.Frame(parent_frame)
tree_frame.grid(row=0, column=1, sticky="nsew")

tree = ttk.Treeview(tree_frame, columns=("Line", "Item", "Quantity", "Item Cost", "Total Cost"), show="headings")
tree.heading("Line", text="Line")
tree.heading("Item", text="Item")
tree.heading("Quantity", text="Quantity")
tree.heading("Item Cost", text="Item Cost")
tree.heading("Total Cost", text="Total Cost")

# Set column widths based on column titles
for column in tree["columns"]:
    header = tree.heading(column)["text"]
    column_width = max(len(header) * 8, tree.column(column, option="minwidth"))
    tree.column(column, width=column_width, minwidth=column_width)

tree.grid(row=0, column=0, sticky="nsew")

# Create labels
labels_frame = tk.Frame(root)
labels_frame.grid(row=1, column=0, sticky="nsew")

subtotal_label = tk.Label(labels_frame, text="Order Subtotal: $0.00")
subtotal_label.grid(row=0, column=0, sticky="w")

total_label = tk.Label(labels_frame, text="Order Total (incl. 13% tax): $0.00")
total_label.grid(row=1, column=0, sticky="w")

# Configure grid weights for resizing
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0)

parent_frame.columnconfigure(0, weight=1)
parent_frame.columnconfigure(1, weight=1)
parent_frame.rowconfigure(0, weight=1)

buttons_frame.columnconfigure(0, weight=1)
buttons_frame.columnconfigure(1, weight=1)
buttons_frame.rowconfigure(0, weight=8)
buttons_frame.rowconfigure(1, weight=8)
buttons_frame.rowconfigure(2, weight=1)
buttons_frame.rowconfigure(3, weight=1)

remove_frame.columnconfigure(0, weight=1)
remove_frame.columnconfigure(1, weight=1)

search_frame.columnconfigure(0, weight=1)
search_frame.columnconfigure(1, weight=1)

tree_frame.columnconfigure(0, weight=1)
tree_frame.rowconfigure(0, weight=1)

labels_frame.columnconfigure(0, weight=1)
labels_frame.rowconfigure(0, weight=1)
labels_frame.rowconfigure(1, weight=1)

# Set minimum size for tree frame
root.update_idletasks()
min_width = tree_frame.winfo_reqwidth()
tree_frame.grid_propagate(0)
tree_frame.config(width=min_width)

# Load items from file
buttons = [button1, button2, button3, button4]
load_items_from_file(os.getcwd() + "\items.txt")

root.mainloop()