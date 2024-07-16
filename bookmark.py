from unstructured.partition.pdf import partition_pdf
from PyPDF2 import PdfReader, PdfWriter
from dicttoxml import dicttoxml
import pymupdf

# Read the original PDF
# input_pdf = PdfReader(f'income-tax-act-1961-amended-by-finance-act-2024.pdf')
pdf_document = pymupdf.open(f'income-tax-act-1961-amended-by-finance-act-2024.pdf')
print(pymupdf.__doc__)
# elements = partition_pdf(filename="income-tax-act-1961-amended-by-finance-act-2024.pdf")
# print("\n\n".join([ str(el) for el in elements]))\
    
# print(input_pdf.outline)
all_files = {}
all_files["pages"] = []
bookmark_list = pdf_document.get_toc(simple=False)
all_bookmark_pages = []
for item in bookmark_list:
    point = item[3].get("view", "FitH,0")
    point = float(point.replace("FitH,", ""))
    all_bookmark_pages.append([item[1], item[2], point])

# print(all_bookmark_pages)
all_bookmark_top = []
no_of_session = 1
for i in range(0, len(all_bookmark_pages)):
    curr_page = all_bookmark_pages[i]
    next_page = all_bookmark_pages[i+1] if (i+1) < len(all_bookmark_pages) else None
    
    title = curr_page[0]
    from_page = curr_page[1]
    from_top = curr_page[2]
    
    pages = []
    if next_page:
        for j in range(from_page, next_page[1]+1):
            _bookmark = dict()
            _bookmark["id"] = no_of_session
            _bookmark["title"] = title
            _bookmark["page"] = j
            if j == from_page:
                _bookmark["top"] = from_top
            if j == next_page[1]:
                _bookmark["bottom"] = next_page[2]
            
            all_bookmark_top.append(_bookmark)
    else:
        _bookmark = dict()
        _bookmark["id"] = no_of_session
        _bookmark["title"] = title
        _bookmark["page"] = from_page
        _bookmark["top"] = from_top
        all_bookmark_top.append(_bookmark)
    
    no_of_session += 1

# for item in all_bookmark_top:
#     print(item)

session_id = 0
final_text = []
for i in range(0, len(all_bookmark_top)):
    print(item)
    item = all_bookmark_top[i]
    next_item = all_bookmark_top[i+1] if (i+1) < len(all_bookmark_top) else None
    
    page = pdf_document.load_page(item.get('page') - 1)
    top = item.get('top', 0)
    bottom = item.get('bottom', page.rect.height)
    top_rect = pymupdf.Rect(0, top, page.rect.width, bottom)
    text = page.get_text("text", clip=top_rect)
    final_text.append(text)
    
    if next_item and int(item.get('id')) == int(next_item.get('id')):
        pass
    else:
        all_files["pages"].append(
            {
                "id": item.get('id'),
                "title" : str(item.get('title')),
                "text" : "\n".join(final_text)
            }
        )
        final_text = []

# for i in range(len(all_bookmark_pages)):
#     curr_page = all_bookmark_pages[i]
#     next_page = all_bookmark_pages[i+1] if (i+1) < len(all_bookmark_pages) else None
#     from_page = curr_page[1]
#     pages = []
#     if next_page:
#         to_page = next_page[1]
#         pages = input_pdf.pages[from_page:to_page+1]
#     else:
#         pages = input_pdf.pages[from_page:]
    
#     print(curr_page, next_page)
#     all_files["pages"].append(
#         {
#             "title" : str(curr_page[0]),
#             "text" : "\n".join([ el.extract_text() for el in pages])
#         }
#     )


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
 
xmlfile = open("updated_dict.xml", "w")
xmlfile.write(xml_decode)
xmlfile.close()
