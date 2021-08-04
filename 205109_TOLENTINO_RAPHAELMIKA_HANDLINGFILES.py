#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# NON-INTERACTIVE CODE CELL. YOU MAY RUN THIS CELL, BUT DO NOT EDIT IT.
# FOR DEMONSTRATION PURPOSES ONLY. DO NOT EDIT.

products = {
    "americano":{"name":"Americano","price":150.00},
    "brewedcoffee":{"name":"Brewed Coffee","price":110.00},
    "cappuccino":{"name":"Cappuccino","price":170.00},
    "dalgona":{"name":"Dalgona","price":170.00},
    "espresso":{"name":"Espresso","price":140.00},
    "frappuccino":{"name":"Frappuccino","price":170.00},
}


# # Problem 1: Product Information Lookup

# In[ ]:


def get_product(code):
    return products[code]

get_product("americano")


# # Problem 2: Product Property Lookup

# In[ ]:


def get_property(code, product_property):
    product_dict = get_product(code)
    return product_dict[product_property]

get_property("espresso", "price")


# # Product 3: The Point-of-Sale Terminal

# In[ ]:


def main():
    total = 0
    orders = {}
    
    while True:
        order = input("Enter your order (Product Code, Quantity): ")

        if order == "/": 
            break
            
        try:    
            order_split = order.split(",")
            code, quantity = [x.strip() for x in order_split]
            price = float(get_property(code, "price"))

            if code in orders:
                total += float(quantity) * price
                new_quantity = float(orders[code]["quantity"]) + float(quantity)
                orders[code]["quantity"] = new_quantity
                orders[code]["subtotal"] = price * new_quantity

            else:
                subtotal =  price * float(quantity)
                total += subtotal

                # if not in dictionary, create new order dict
                orders[code] = {"name" : get_property(code, "name"), "quantity" : float(quantity), "subtotal" : subtotal} 
        
        except:
            print("\nPlease follow order format to avoid errors\n")

    # receipt generation
    receipt_string = "\n==\nCODE\t\t\tNAME\t\t\tQUANTITY\t\t\tSUBTOTAL\n\n"

    for key, values in sorted(orders.items()):
        receipt_string += "{0: <15} {1: <15} {2: <19} {3:}\n".format(key, values["name"], values["quantity"], values["subtotal"])

    receipt_string += f"\nTotal:\t\t\t\t\t\t\t\t\t\t\t\t{total}\n=="

    # write to receipt
    with open("receipt.txt", "w+") as f:
        f.write(receipt_string)
        
main()


# # Problem 4: Final Instructions

# In[ ]:




