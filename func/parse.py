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

def get_summary(jumbled_text, focus):
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

    context = f"""Read the following text and condense it to encapsulate the main topics 
    and contents. For math equations/formulas, rather than outputting the characters of 
    the formula (like P(A∣B)= P(A∩B)/P(B)), u should instead, write: "The probability of A
    given B equals the probability of A and B occurring together divided by the probability 
    of B." (this is because the text you write out will be used with a text-to-speech model). 
    Please go in depth on important concepts. Here is the text: {jumbled_text}, make sure to
    focus on: {focus}.
    """

    response = client.chat.completions.create(
        messages=[{"role":"user", "content":context}],
        model="gpt-4o-mini",
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    # file = "func/pdf/102-combinatorial-problems.pdf"
    file = "func/pdf/Quant guide (SBC).pdf"
    start, end = 5, 8
    print(get_summary(get_jumbled_text(file, start, end), "Formulas I need to know"))
