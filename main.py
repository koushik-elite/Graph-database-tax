# from unstructured.partition.pdf import partition_pdf
from PyPDF2 import PdfReader, PdfWriter
from dicttoxml import dicttoxml

# Read the original PDF
input_pdf = PdfReader(f'income-tax-act-1961-amended-by-finance-act-2024.pdf')


# elements = partition_pdf(filename="income-tax-act-1961-amended-by-finance-act-2024.pdf")
# print("\n\n".join([ str(el) for el in elements]))\
    
# print(input_pdf.outline)
all_files = {}
all_files["pages"] = []
bookmark_list = input_pdf.outline
all_bookmark_pages = []
for item in bookmark_list:
    if isinstance(item, list): # a list is for the children of last item
        pass
    else:
        page_index = input_pdf.get_destination_page_number(item)
        all_bookmark_pages.append([item.title, page_index])

# print(all_bookmark_pages)

for i in range(len(all_bookmark_pages)):
    curr_page = all_bookmark_pages[i]
    next_page = all_bookmark_pages[i+1] if (i+1) < len(all_bookmark_pages) else None
    from_page = curr_page[1]
    pages = []
    if next_page:
        to_page = next_page[1]
        pages = input_pdf.pages[from_page:to_page+1]
    else:
        pages = input_pdf.pages[from_page:]
    
    print(curr_page, next_page)
    all_files["pages"].append(
        {
            "title" : str(curr_page[0]),
            "text" : "\n".join([ el.extract_text() for el in pages])
        }
    )
    # all_files["title"] = curr_page[0]
    # all_files[curr_page[0]] = "\n\n".join([ el.extract_text() for el in pages])
    # print(curr_page[0]) 
    # print("\n\n")
    # print(all_files[curr_page[0]]) 
    # print("----------------------------------------------------------------------------------------")
    # break

# for item in bookmark_list:
#     if isinstance(item, list): # a list is for the children of last item
#         pass
#     else:
#         page_index = input_pdf.get_destination_page_number(item)
#         print(item.title, page_index)
# all_pages = len(input_pdf.pages)

# print(f"All Len {all_pages} -----------------------------------------------------------------------")
# for page in input_pdf.pages:
#     print(page.extract_text()) 
#     print("\n\n")

xml = dicttoxml(all_files)
xml_decode = xml.decode()
 
xmlfile = open("dict.xml", "w")
xmlfile.write(xml_decode)
xmlfile.close()
