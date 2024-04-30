#need indexes 1,2,3,6
#


import csv

def read_csv_to_list(filename):
    """
    Read data from a CSV file and save it to a list of lists.

    Args:
    - filename (str): The path to the CSV file.

    Returns:
    - data (list): A list of lists containing the data from the CSV file.
    """
    data = []
    with open(filename, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    return data

def write_list_to_text(data, filename):
    """
    Write data from a list of lists to a text file.

    Args:
    - data (list): A list of lists containing the data.
    - filename (str): The path to the output text file.
    """
    with open(filename, 'w') as file:
        for row in data:
            file.write(', '.join(row) + '\n')








input_filename = 'Item_Pricing_Details.csv'
output_text_filename = 'output.txt'

# Read data from CSV to a list of lists
rawdata = read_csv_to_list(input_filename)
rawdata.pop(0)
newdata = []

for i in range(len(rawdata)):
    if rawdata[i][3] != '2':
        newdata.append([rawdata[i][1], rawdata[i][2], rawdata[i][6]])





checkfilename = 'Item_Pricing.csv'
rawcheckdata = read_csv_to_list(checkfilename)
rawcheckdata.pop(0)
checkdata = []

for i in range(len(rawcheckdata)):
    checkdata.append([rawcheckdata[i][1], rawcheckdata[i][2], rawcheckdata[i][3]])

newdict = {}
for i in checkdata:
    #add pricelist
    if i[1] not in newdict:
        newdict[i[1]] = {}
    
    #add item
    if i[0] not in newdict[i[1]]:
        newdict[i[1]][i[0]] = i[2]

"""
for key in newdict:
    print(f"\n\n\n<<<< {key} >>>>\n\n\n")
    for k,v in newdict[key].items():
        print(k + " : " + v)
print("\n\n\n<<<< KEEYYYYY >>>>\n\n\n")
for k,v in newdict["LEG"].items():
    print(k + " : " + v)
"""

# print("Data from CSV:")
# for row in newdata:
#     print(row)



outlists = {pricelist : [] for pricelist in newdict.keys()}
for i in range(len(newdata)):
    # try:
        pricelist = newdata[i][1]

        itemcode = newdata[i][0]
        itemdescription = newdict[pricelist][itemcode]
        itemcost = newdata[i][2]
        
        if itemdescription == "":
            itemdescription = "No Description"
        itemdescription.replace(",","")

        outlists[pricelist].append(", ".join([itemcode, itemdescription, itemcost]))
    # except:
    #     print("EXCEPTION" + " , ".join(rawcheckdata[i]))


# for i in newdata:
#     print(i)

# for k, v in outlists.items():
#     print(f"\n <<<< {k} >>>> \n")
#     for i in v:
#         print(i)

for k, v in outlists.items():
    print(f"\n <<<< {k} >>>> \n")

    with open(k + ".txt", 'w') as file:
        for line in v:
            file.write(line + '\n')


# Write data from list of lists to CSV

# write_list_to_text(data, output_text_filename)
# print(f"Data written to {output_text_filename}.")
