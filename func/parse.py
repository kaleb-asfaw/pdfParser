import PyPDF2

def read(file, start, end):
    '''
    This function's purpose is to receive a file, and desired page range, and 
    return the text in the form of a dictionary.

    Inputs: 

        -> file (str): path to pdf
        -> start (int): start page to read
        -> end (int): end page to read

    Output:

        -> pages (dict): schema --> {page # : text}

    '''
    
    try:
        reader = PyPDF2.PdfReader(file)
    except:
        raise ValueError(f"The file path {file} could not be found")
    pages = {}
    for p in range(start, end+1):
        page = reader.pages[p]
        pages[p] = page.extract_text()
    
    return pages

if __name__ == "__main__":
    file = "pdf/HUTC Case Documents.pdf"
    start, end = 1, 5
    # print(read(file, start, end))