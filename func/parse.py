import PyPDF2
import wordninja


def remove_whitespace(text):
    '''
    Splits a jumbled text string into an array where each element
    is a word.
    '''
    return wordninja.split(text)

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
    texts = {}
    for p in range(start, end+1):
        page = reader.pages[p]
        texts[p] = remove_whitespace(page.extract_text())
    
    return texts


def format(texts):
    '''
    This function's purpose is to receive a file, and desired page range, and 
    return the text in the form of a dictionary.

    Inputs: 

        -> texts (dict): as returned in read function above

    Output:

        -> pages (list): a list of each page's text as a string

    '''
    pages = []
    for page, text in texts.items():
        p = ""
        for word in text:
            p += f"{word} "
        pages.append(p)
    return pages


def get_text(file, start, end):
    '''
    Run this function, which takes in the filepath, as well as first 
    and last page to read/summarize.

    Inputs: 

        -> file (str): path to pdf
        -> start (int): start page to read
        -> end (int): end page to read

    Output:

        -> pages (list): a list of each page's text as a string
    '''
    pages = format(read(file, start, end))
    return pages

def get_jumbled_text(file, start, end):
    '''
    Run this function, which takes in the filepath, as well as first
    and last page to read/summarize.

    Inputs: 

        -> file (str): path to pdf
        -> start (int): start page to read
        -> end (int): end page to read

    Output:

        -> txt (str): a long, unspaced string of text (input for LLM)
    '''
    pages = read(file, start, end)
    txt = ''
    for page, text in pages.items():
        for word in text:
            txt += word
    return txt


if __name__ == "__main__":
    file = "func/pdf/HUTC Case Document.pdf"
    start, end = 1, 5
    print(get_text(file, start, end))
    print("________________________")
    print(get_jumbled_text(file, start, end))
