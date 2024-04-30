import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import os

TAX_RATE = 0.13
master_item_dict = {}
selection = "LEG"

def initialize_master_item_dict():
    cwd = os.getcwd()
    for filename in os.listdir(cwd + "\pricelists"):
        print(filename)
        with open("pricelists\\" + filename, "r") as file:
             newdict= {}
             for line in file:
                 item_code, item_name, item_cost = line.strip().split(", ")
                 newdict[item_code] = {"name": item_name, "cost": float(item_cost)}
             master_item_dict[filename[:-4]] = newdict.copy()

def in_all_codes(item_code) -> bool:
    for pricelist in master_item_dict:
        print(item_code)
        print(type(pricelist))
        print()
        if item_code in master_item_dict[pricelist]:
            return True
    return False

def configure_quick_selections():
    """
    read from quickselect
    for each text file create a button
    if the textfile has items on multiple lines
    """
    pass

def button_clicked(item_code):
    if in_all_codes(item_code):
        add_item(master_item_dict[selection][item_code])
    else:
        messagebox.showerror("Item Not Found", "Item code not found")

def search():
    searched_code = search_entry.get()
    if in_all_codes(searched_code):
        add_item(searched_code)
    else:
        messagebox.showerror("Item Not Found", "Item code not found")

def add_item(item_code):
    item_info = master_item_dict[selection][item_code]
    for child in tree.get_children():
        if tree.item(child, "values")[1] == item_info["name"]:
            quantity = int(tree.item(child, "values")[2]) + 1
            total_cost = item_info["cost"] * quantity
            tree.item(child, values=(tree.item(child, "values")[0], item_info["name"], quantity, item_info["cost"], total_cost))
            calculate_order_totals()
            return
    line_num = len(tree.get_children()) + 1
    tree.insert("", "end", values=(line_num, item_info["name"], 1, item_info["cost"], item_info["cost"]))
    calculate_order_totals()

def remove_item():
    selected_line = int(line_number_entry.get())
    for child in tree.get_children():
        line_num = int(tree.item(child, "values")[0])
        if line_num == selected_line:
            tree.delete(child)
    calculate_order_totals()

def calculate_order_totals():
    subtotal = 0
    for child in tree.get_children():
        subtotal += float(tree.item(child, "values")[4])
    tax = subtotal * TAX_RATE
    total = subtotal + tax
    subtotal_label.config(text=f"Order Subtotal: ${subtotal:.2f}")
    total_label.config(text=f"Order Total (incl. 13% tax): ${total:.2f}")



root = tk.Tk()
root.title("Till")
root.geometry("600x300")

# Create parent frame
parent_frame = tk.Frame(root)
parent_frame.grid(row=0, column=0, sticky="nsew")

# Initialize master item dictionary and get the first four items
initialize_master_item_dict()
first_four_items = []

# Create frame for buttons
buttons_frame = tk.Frame(parent_frame)
buttons_frame.grid(row=0, column=0, sticky="nsew")

# Create buttons with first four items
buttons = []
for i, item_code in enumerate(first_four_items):
    item_info = master_item_dict[item_code] # not gonna work
    button = tk.Button(buttons_frame, text=item_info["name"], command=lambda code=item_code: button_clicked(code))
    button.grid(row=i//2, column=i%2, sticky="nsew")
    buttons.append(button)

# Create frame for search bar
search_frame = tk.Frame(buttons_frame)
search_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")

search_button = tk.Button(search_frame, text="Search", command=search)
search_button.grid(row=0, column=0, sticky="nsew", padx=10)

search_entry = tk.Entry(search_frame, width=5)
search_entry.grid(row=0, column=1, sticky="nsew", padx=5)

# Create frame for remove bar
remove_frame = tk.Frame(buttons_frame)
remove_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")

remove_button = tk.Button(remove_frame, text="Remove Item", command=remove_item)
remove_button.grid(row=0, column=0, sticky="nsew", padx=10)

line_number_entry = tk.Entry(remove_frame, width=5)
line_number_entry.grid(row=0, column=1, sticky="nsew", padx=5)

# Create frame for other pricelists
pricelist_search_frame = tk.Frame(buttons_frame)
pricelist_search_frame.grid(row=4, column=0, columnspan=2, sticky="nsew")

pricelist_search_entry = tk.Entry(pricelist_search_frame, width=5)
pricelist_search_entry.grid(row=0, column=1, sticky="nsew", padx=5)

pricelist_search_button = tk.Button(pricelist_search_frame, text="Pricelist", command=lambda code=pricelist_search_entry.get() : selectpricelist(code))
pricelist_search_button.grid(row=0, column=0, sticky="nsew", padx=10)

# Create frame for pricelist selection
pricelist_frame = tk.Frame(buttons_frame)
pricelist_frame.grid(row=5, column=0, columnspan=2, sticky="nsew")

pricelist_button1 = tk.Button(pricelist_frame, text="LEG", relief="sunken", padx=20)
pricelist_button1.grid(row=0, column=0, sticky="nsew")

pricelist_button2 = tk.Button(pricelist_frame, text="BACPKG", relief="raised", padx=20)
pricelist_button2.grid(row=0, column=1, sticky="nsew")

## pricelist_button3 = tk.Button(remove_frame, text="temp", command=remove_item)
## pricelist_button3.grid(row=0, column=2, sticky="nsew")

def selectpricelist(pricelist: str):
    global selection
    if pricelist == "LEG":
        selection = "LEG"
        pricelist_button1.config(relief="sunken")
        pricelist_button2.config(relief="raised")
    elif pricelist == "BACPKG":
        selection = "BACPKG"
        pricelist_button1.config(relief="raised")
        pricelist_button2.config(relief="sunken")
    else:
        cwd = os.getcwd()
        for pricelistfile in os.listdir(cwd + "\pricelists"):
            pricelist = pricelistfile.replace(".txt", "")
        pricelist_button1.config(relief="raised")
        pricelist_button2.config(relief="raised")

pricelist_button1.config(command=lambda : selectpricelist("LEG"))
pricelist_button2.config(command=lambda : selectpricelist("BACPKG"))

# Create frame for treeview
tree_frame = tk.Frame(parent_frame)
tree_frame.grid(row=0, column=1, sticky="nsew")

tree = ttk.Treeview(tree_frame, columns=("Line", "Item", "Quantity", "Item Cost", "Total Cost"), show="headings")
tree.heading("Line", text="Line")
tree.heading("Item", text="Item")
tree.heading("Quantity", text="Qty")
tree.heading("Item Cost", text="Cost")
tree.heading("Total Cost", text="Total Cost")

# Set column widths based on column titles
tree.column("Line", width=20, minwidth=20)
tree.column("Item", width=196, minwidth=32)
tree.column("Quantity", width=20, minwidth=20)
tree.column("Item Cost", width=32, minwidth=32)
tree.column("Total Cost", width=48, minwidth=32)
# for column in tree["columns"]:
#     header = tree.heading(column)["text"]
#     column_width = max(len(header) * 8, tree.column(column, option="minwidth"))
#     tree.column(column, width=column_width, minwidth=column_width)

tree.grid(row=0, column=0, sticky="nsew")

# Create labels
labels_frame = tk.Frame(root)
labels_frame.grid(row=1, column=0, sticky="nsew")

subtotal_label = tk.Label(labels_frame, text="Order Subtotal: $0.00")
subtotal_label.grid(row=0, column=0, sticky="e", padx=40)

total_label = tk.Label(labels_frame, text="Order Total (incl. 13% tax): $0.00")
total_label.grid(row=0, column=1, sticky="e")

# Configure grid weights for resizing
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0)

parent_frame.columnconfigure(0, weight=1)
parent_frame.columnconfigure(1, weight=1)
parent_frame.rowconfigure(0, weight=1)

buttons_frame.columnconfigure(0, weight=1)
buttons_frame.columnconfigure(1, weight=1)
buttons_frame.rowconfigure(0, weight=1)
buttons_frame.rowconfigure(1, weight=1)
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


root.mainloop()