import os
import PyPDF2, wordninja
from openai import OpenAI

openai_key = os.getenv('OPENAI_KEY')


if not openai_key:
    raise EnvironmentError("Environment variable for OpenAI key was not set")

client = OpenAI(api_key = openai_key)

def remove_whitespace(text):
    '''
    Splits a jumbled text string into an array where each element
    is a word.
    '''
    return wordninja.split(text)

def read(file, start=None, end=None):
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
        if start is None or end is None:
            start, end = 1, len(reader.pages)
        elif start < 1 or end >= len(reader.pages):
            raise ValueError("Please enter pages that exist in your pdf.")
    except:
        raise ValueError(f"The file path {file} could not be found")
    texts = {}
    for p in range(start, end):
        if reader.pages[p]:
            page = reader.pages[p]
            texts[p] = remove_whitespace(page.extract_text())
        else:
            break
    
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


def get_text(file, start=None, end=None):
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

def get_jumbled_text(file, start=None, end=None):
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

def get_summary(jumbled_text=None, focus=None):
    """
    This function should return a viable summary for the pdf input by 
    the user. 

    Inputs: 

        -> jumbled_text (str):  A long, unspaced text string
        -> focus (str): A string of areas of concentration for the summary

    Output:

        -> summary (str): Summary of pdf that will be input to TTS for 
        speech output
   """

    if focus:
        context = f"""Read the following text and condense it to encapsulate the main topics 
        and contents. For math equations/formulas, rather than outputting the characters of 
        the formula (like P(A∣B)= P(A∩B)/P(B)), u should instead, write out the formula's
        pronunciation (this is because the text you write out will be used with a text-to-
        speech model). Please go in depth on important concepts. Here is the text: 
        {jumbled_text}, make sure to focus on: {focus}.
        """
    else:
        context = f"""Read the following text and condense it to encapsulate the main topics 
        and contents. For math equations/formulas, rather than outputting the characters of 
        the formula (like P(A∣B)= P(A∩B)/P(B)), u should instead, write out the formula's
        pronunciation (this is because the text you write out will be used with a text-to-
        speech model). Please go in depth on important concepts. Here is the text: 
        {jumbled_text}.
        """

    response = client.chat.completions.create(
        messages=[{"role":"user", "content":context}],
        model="gpt-4o-mini",
    )
    return response.choices[0].message.content.strip()

def get_summary_from_upload(file, start=None, end=None, focus=None):
    """
    function to be called from app.py
    functino should take the uploaded pdf from pdf_placeholder and return summary text
    currently using filler text for proof of concept
    TODO: make this function work
    """
    return get_summary(get_jumbled_text(file, start, end), focus)

if __name__ == "__main__":

    print(os.getcwd())
    file_path = "func/recordings/maudirac07@gmail.com/Perfect_Proof_of_Islam_and_Absolute_Islamic_Topics.pdf"
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file path {file_path} does not exist.")
    try:
        print(get_summary(get_jumbled_text(file_path)))
    except Exception as e:
        print("An error occurred:", e)

# if __name__ == "__main__":
#     file = "func/pdf/Quant guide (SBC).pdf"
#     start, end = 5, 8
#     print(get_summary(get_jumbled_text(file)))
