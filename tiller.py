#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import os
import json


#### SETUP ####
#check display

if os.environ.get('DISPLAY','') == '':
    #print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

os.chdir("/home/pi/Desktop/Cashier-Till")

#### FINISH SETUP ####


TAX_RATE = 0.13
master_item_dict = {}
master_quickselect_dict = {}
popup_windows = []
selection = "LEG"

def initialize_master_item_dict():
    cwd = os.getcwd()
    for filename in os.listdir(cwd + "/pricelists"):
        # print(filename)
        with open("pricelists/" + filename, "r", errors='ignore') as file:
             newdict= {}
             for line in file:
                 item_code, item_name, item_cost = line.strip().split(", ")
                 newdict[item_code] = {"name": item_name, "cost": float(item_cost)}
             master_item_dict[filename[:-4]] = newdict.copy()

def initialize_quickselect():
    with open("quickselects.json", "r") as json_file:
        global master_quickselect_dict 
        master_quickselect_dict = json.load(json_file)

def in_all_codes(item_code) -> bool:
    for pricelist in master_item_dict:
        # print(item_code)
        # print(type(pricelist))
        # print()
        if item_code in master_item_dict[pricelist]:
            return True
    return False

def button_clicked(item_code):
    if in_all_codes(item_code):
        add_item(item_code)
    else:
        messagebox.showerror("Item Not Found", "Item code not found")

def search():
    searched_code = search_entry.get()
    if in_all_codes(searched_code.capitalize()):
        add_item(searched_code)
    else:
        messagebox.showerror("Item Not Found", "Item code not found")


def remove_item(item_code):
    for child in tree.get_children():
        if tree.item(child, "values")[4] == item_code:
            quantity = int(tree.item(child, "values")[1]) - 1
            if quantity <= 0:
                tree.delete(child)
            else:
                item_cost = float(tree.item(child, "values")[2])
                tree.item(child, values=(tree.item(child, "values")[0], quantity, tree.item(child, "values")[2], item_cost * quantity, item_code))
 
def add_item(item_code):
    item_info = master_item_dict[selection][item_code]
    desc = item_info["name"]
    if desc == "No Description" and item_code[-5:] == "ACUST":
        desc = "Customer Name"
    for child in tree.get_children():
        if tree.item(child, "values")[0] == desc:
            # Item already exists, increase quantity and update total cost
            quantity = int(tree.item(child, "values")[1]) + 1
            total_cost = item_info["cost"] * quantity
            tree.item(child, values=(desc, quantity, selection, item_info["cost"], total_cost, item_code))  # Add item code to values
            calculate_order_totals()
            return
    # Item does not exist, insert a new entry
    tree.insert("", "end", values=(desc, 1, selection, item_info["cost"], item_info["cost"], item_code))  # Add item code to values
    calculate_order_totals()

def remove_selected_item():
    selected_item = tree.selection()  # Get the ID of the selected item
    if selected_item:  # Check if an item is selected
        item_info = tree.item(selected_item, "values")
        remove_item(item_info[4])
        calculate_order_totals()
    else:
        messagebox.showerror("No Item Selected", "Please select an item to Remove")

def add_additional_item():
    selected_item = tree.selection()
    if selected_item:
        item_info = tree.item(selected_item, "values")
        add_item(item_info[4])
        calculate_order_totals()
    else:
        messagebox.showerror("No Item Selected", "Please select an item to Add")

def calculate_order_totals():
    subtotal = 0
    for child in tree.get_children():
        subtotal += float(tree.item(child, "values")[3])
    tax = subtotal * TAX_RATE
    total = subtotal + tax
    subtotal_label.config(text=f"Order Subtotal: ${subtotal:.2f}")
    total_label.config(text=f"Order Total (incl. 13% tax): ${total:.2f}")



def close_toplevel_windows(event, popup_window):
    # Check if the click occurred outside of any Toplevel windows
    x, y = event.x_root, event.y_root

    # Get the geometry of the popup window
    popup_geometry = popup_window.geometry()

    # Extract the width and height from the popup geometry string
    popup_width = int(popup_geometry.split("x")[0])
    popup_height = int(popup_geometry.split("x")[1].split("+")[0])

    # Get the x and y position of the top-left corner of the popup window
    popup_x = int(popup_geometry.split("+")[1])
    popup_y = int(popup_geometry.split("+")[2])

    # Calculate the x and y positions of the bottom-right corner of the popup window
    popup_bottom_right_x = popup_x + popup_width
    popup_bottom_right_y = popup_y + popup_height

    # Check if the click occurred outside of the popup window boundaries
    if not (popup_x <= x <= popup_bottom_right_x and popup_y <= y <= popup_bottom_right_y):
        popup_window.destroy()

def show_price_list_popup():
    # Create the popup window
    popup_window = tk.Toplevel(root)
    popup_window.title("Select Price List")
    popup_window.grab_set()  # Make the popup window modal

    # Add label at the top
    label = tk.Label(popup_window, text="Select a Price List", font=("Arial", 14, "bold"))
    label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
    
    # Define the list of price lists to display
    pricelists = [pl for pl in master_item_dict.keys() if pl not in ["LEG", "BACPKG"]]

    # Create buttons for each price list
    for i, pricelist in enumerate(pricelists):
        button = tk.Button(popup_window, text=pricelist, padx=20, pady=10, wraplength=150, command=lambda pl=pricelist: selectpricelist(pl, popup_window))
        button.grid(row=(i // 3)+1, column=i % 3, padx=10, pady=10, sticky="nsew")

    # Configure grid weights for resizing
    for i in range(len(pricelists)):
        popup_window.grid_rowconfigure(i // 3, weight=1)
        popup_window.grid_columnconfigure(i % 3, weight=1)

    # Bind focus event to destroy the popup window when root window receives focus
    popup_window.bind("<Button-1>", lambda event, popup_window=popup_window: close_toplevel_windows(event, popup_window))

def show_search_popup():
    # Create the popup window
    popup_window = tk.Toplevel(root)
    popup_window.title("Search by Description")
    popup_window.grab_set()  # Make the popup window modal
    popup_window.geometry(f"{500}x{500}+300+50")

    # Configure row and column weights for resizing
    popup_window.columnconfigure(0, weight=1)
    popup_window.rowconfigure(2, weight=1)

    def search_by_description():
        description_tree.delete(*description_tree.get_children())

        # Get the search query from the entry widget
        query = description_entry.get()

        # Perform the search
        search_results = []

        for pricelist in master_item_dict.values():
            for item_code, item_info in pricelist.items():
                if query.lower() in item_info["name"].lower():
                    search_results.append((item_code, item_info["name"]))

        # Display search results in the Treeview
        for i, (item_code, item_name) in enumerate(search_results):
            description_tree.insert("", "end", values=(item_code, item_name))

    def add_selected_item():
        # Get the selected item from the Treeview
        selected_item = description_tree.focus()
        if selected_item:
            item_code, item_name = description_tree.item(selected_item, "values")

            # Add the selected item to the main order Treeview
            add_item(item_code)

            # Close the popup window after adding the item
            popup_window.destroy()
    
    

    # Entry widget for search query
    description_entry = tk.Entry(popup_window)
    description_entry.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    # Button to trigger search
    search_button = tk.Button(popup_window, text="Search", command=search_by_description)
    search_button.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

    # Treeview to display search results
    description_tree = ttk.Treeview(popup_window, columns=("Item Code", "Item Name"), show="headings")
    description_tree.heading("Item Code", text="Item Code")
    description_tree.heading("Item Name", text="Item Name")

    description_tree.column("Item Code", width=10, minwidth=10)
    description_tree.column("Item Name", width=60, minwidth=20)

    description_tree.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")


    # Button to add selected item to the main order Treeview
    add_button = tk.Button(popup_window, text="Add", command=add_selected_item)
    add_button.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

    # Bind focus event to destroy the popup window when root window receives focus
    popup_window.bind("<Button-1>", lambda event, popup_window=popup_window : close_toplevel_windows(event, popup_window))



root = tk.Tk()
root.title("Till")


#################################################################################
#                                QUICKSELECT                                    #
#################################################################################

def add_items_to_order(item_codes):
    # Function to add multiple items to the order
    for item_code in item_codes:
        add_item(item_code)

def handle_list_button_click(item_codes):
    # Close all popup windows
    for popup_window in popup_windows:
        popup_window.destroy()
    # Add items to the order
    add_items_to_order(item_codes)

def handle_string_button_click(item_code):
    # Close all popup windows
    for popup_window in popup_windows:
        popup_window.destroy()
    # Add item to the order
    add_item(item_code)

def handle_click(key, value):
    if isinstance(value, dict):
        # If value is a dictionary, create a popup window for it
        create_popup_for_dict(value)
    elif isinstance(value, list):
        # If value is a list, add items to the order
        handle_list_button_click(value)
    elif isinstance(value, str):
        # If value is a string, add the item to the order
        handle_string_button_click(value)
    else:
        # Handle other data types if necessary
        pass

def create_popup_for_dict(master_dict):
    popup_window = tk.Toplevel(root)
    popup_window.attributes('-fullscreen', True)
    popup_windows.append(popup_window)

    def handle_dict_button_click(key):
        nested_dict = master_dict[key]
        create_popup_for_dict(nested_dict)

    def handle_list_button_click(item_codes):
        popup_window.destroy()
        add_items_to_order(item_codes)

    def handle_string_button_click(item_code):
        popup_window.destroy()
        add_item(item_code)

    row = 0
    kvss = [[k,v] for k,v in master_dict.items()]
    a = int((len(kvss))**0.5)
    for i in range(len(kvss)):
        k, v = kvss[i][0], kvss[i][1]
        button = ttk.Button(popup_window, text=k, command=lambda kk=k, v=v: handle_click(kk, v))
        button.grid(row=i%a, column=i//a, padx=10, pady=5, ipadx=10, ipady=10, sticky="nsew")

    # Creating Close Button
    close_button = ttk.Button(popup_window, text="Close", command=popup_window.destroy)
    close_button.grid(row=(len(kvss)//a)+1, column=0, columnspan=(len(kvss)//a), padx=10, pady=5, ipadx=20, ipady=20,  sticky="ew")

#################################################################################
#                                QUICKSELECT                                    #
#################################################################################

# Set the window size to fill the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()# - 65
root.geometry(f"{screen_width}x{screen_height}+0+0")

# Expand the window to fullscreen
root.attributes('-fullscreen', True)

# Create parent frame
parent_frame = tk.Frame(root)
parent_frame.grid(row=0, column=0, sticky="nsew")

# Initialize master item dictionary and get the first four items
initialize_master_item_dict()

initialize_quickselect()

# Create frame for treeview
tree_frame = tk.Frame(parent_frame)
tree_frame.grid(row=0, column=1, sticky="nsew", pady=10, padx=10)

tree = ttk.Treeview(tree_frame, columns=("Item", "Quantity", "Pricelist", "Item Cost", "Total Cost"), show="headings")
tree.heading("Item", text="Item")
tree.heading("Quantity", text="Qty")
tree.heading("Pricelist", text="P/L")
tree.heading("Item Cost", text="Cost")
tree.heading("Total Cost", text="Total Cost")

# Set column widths based on column titles
tree.column("Item", width=196, minwidth=32)
tree.column("Quantity", width=20, minwidth=20)
tree.column("Pricelist", width=20, minwidth=20)
tree.column("Item Cost", width=32, minwidth=32)
tree.column("Total Cost", width=48, minwidth=32)

tree.grid(row=0, column=0, sticky="nsew")

# Create a vertical scrollbar and link it to the treeview
scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky="ns")

# Create frame for buttons
buttons_frame = tk.Frame(parent_frame)
buttons_frame.grid(row=0, column=0, sticky="nsew", pady=0, padx=0)

kvs = [[k,v] for k,v in master_quickselect_dict.items()]
for i in range(len(kvs)):
    item_name = kvs[i][0]
    button = tk.Button(buttons_frame, text=item_name, padx=20, pady=10, wraplength=150, command=lambda code=kvs[i][1]: create_popup_for_dict(code))
    # TODO uncomment and implement - title at top of popup showing the "folderpath"
    # button = tk.Button(buttons_frame, text=item_name, padx=20, pady=10, wraplength=150, command=lambda code=(kvs[i][1], item_name): create_popup_for_dict(*code))
    button.grid(row=i%3, column=i//3, sticky="nsew")

# # Configure grid weights for resizing
buttons_frame.columnconfigure(0, weight=1, uniform="buttons_col")
buttons_frame.columnconfigure(1, weight=1, uniform="buttons_col")
buttons_frame.rowconfigure(0, weight=1, uniform="buttons_row")
buttons_frame.rowconfigure(1, weight=1, uniform="buttons_row")
buttons_frame.rowconfigure(2, weight=1, uniform="buttons_row")


# Create frame for search bar
search_frame = tk.Frame(buttons_frame)
search_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=10, padx=10)

search_button = tk.Button(search_frame, text="Search via Description", pady=10, command=show_search_popup)
search_button.grid(row=0, column=0, sticky="nsew", padx=10)

# search_entry = tk.Entry(search_frame, width=5)
# search_entry.grid(row=0, column=1, sticky="nsew", padx=5)

# Create frame for remove bar
remove_frame = tk.Frame(buttons_frame, pady=10, padx=10)
remove_frame.grid(row=4, column=0, columnspan=2, sticky="nsew")

remove_button = tk.Button(remove_frame, text="Remove Selected Item", pady=20, command=remove_selected_item)
remove_button.grid(row=0, column=0, sticky="nsew")

# Add Selected Item Button
add_selected_button = tk.Button(remove_frame, text="Add Selected Item", pady=20, command=add_additional_item)
add_selected_button.grid(row=0, column=1, sticky="nsew")


# Create frame for other pricelists
pricelist_search_frame = tk.Frame(buttons_frame)
pricelist_search_frame.grid(row=5, column=0, columnspan=2, sticky="nsew")

pricelist_search_button = tk.Button(pricelist_search_frame, text="Select Another Pricelist", command=show_price_list_popup)
pricelist_search_button.grid(row=0, column=0, sticky="nsew", padx=10)

# Create frame for pricelist selection
pricelist_frame = tk.Frame(buttons_frame)
pricelist_frame.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=10, padx=10)

pricelist_button1 = tk.Button(pricelist_frame, text="LEG", relief="sunken", padx=10)
pricelist_button1.grid(row=0, column=0, sticky="nsew", ipadx=10, ipady=10)

pricelist_button2 = tk.Button(pricelist_frame, text="BACPKG", relief="raised", padx=10)
pricelist_button2.grid(row=0, column=1, sticky="nsew", ipadx=10, ipady=10)

pricelist_button3 = tk.Button(pricelist_frame, text="DFT", relief="raised", padx=10)
pricelist_button3.grid(row=0, column=2, sticky="nsew", ipadx=10, ipady=10, padx=10)


def selectpricelist(pricelist: str, popup_window=None):
    print(pricelist)
    global selection
    if pricelist not in master_item_dict.keys():
        return
    if pricelist == "LEG":
        selection = "LEG"
        pricelist_button1.config(relief="sunken")
        pricelist_button2.config(relief="raised")
        pricelist_button3.config(relief="raised")
    elif pricelist == "BACPKG":
        selection = "BACPKG"
        pricelist_button1.config(relief="raised")
        pricelist_button2.config(relief="sunken")
        pricelist_button3.config(relief="raised")
    else:
        selection = pricelist
        pricelist_button3.config(text=pricelist)
        pricelist_button1.config(relief="raised")
        pricelist_button2.config(relief="raised")
        pricelist_button3.config(relief="sunken")
    if popup_window is not None:
        popup_window.destroy()

pricelist_button1.config(command=lambda : selectpricelist(pricelist_button1.cget("text")))
pricelist_button2.config(command=lambda : selectpricelist(pricelist_button2.cget("text")))
pricelist_button3.config(command=lambda : selectpricelist(pricelist_button3.cget("text")))

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

search_frame.columnconfigure(0, weight=1, uniform="buttons_col")
search_frame.columnconfigure(1, weight=1, uniform="buttons_row")

tree_frame.columnconfigure(0, weight=1)
tree_frame.rowconfigure(0, weight=1)

labels_frame.columnconfigure(0, weight=1)
labels_frame.rowconfigure(0, weight=1)
labels_frame.rowconfigure(1, weight=1)

# Set minimum size for tree frame
root.update_idletasks()
min_width = tree_frame.winfo_reqwidth()
tree_frame.grid_propagate(0)

buttons_frame.config(width = 300)
tree_frame.config(width=600)

tree.style = ttk.Style()
tree.style.configure("Treeview", rowheight=50)

root.mainloop()