import os
import PyPDF2, wordninja
from openai import OpenAI

openai_key = os.getenv('OPENAI_KEY')

# TEMPORARILY BYPASSING OPENAI KEY FOR PROOF OF CONCEPT
# if not openai_key:
#     raise EnvironmentError("Environment variable for OpenAI key was not set")

# client = OpenAI(api_key = openai_key)

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

def get_summary_from_upload():
    """
    function to be called from app.py
    functino should take the uploaded pdf from pdf_placeholder and return summary text
    currently using filler text for proof of concept
    TODO: make this function work
    """
    # get_jumbled_text('pdf_placeholder/temp.pdf', 1, 1)
    return """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor erat in venenatis euismod. Nam vestibulum efficitur tortor, tincidunt condimentum nunc cursus in. Aliquam sit amet interdum odio, nec tincidunt sem. Fusce ullamcorper diam a sapien tincidunt, eget venenatis dui condimentum. Vivamus auctor, sem id ultricies aliquam, lorem tellus tincidunt elit, sit amet pretium elit velit eu ipsum. Fusce purus justo, elementum sagittis gravida in, lobortis sed sapien. In porttitor, orci egestas condimentum elementum, dolor ipsum sagittis nisi, et bibendum neque orci vitae ligula. Duis pretium ac dui at cursus. Nam nunc quam, tempor nec leo ultricies, pharetra posuere turpis. Sed fermentum, mi malesuada cursus faucibus, orci ligula ullamcorper risus, ac condimentum erat lorem non lacus. Aenean dictum quam sit amet placerat porttitor. Cras vitae rhoncus ante, ut porta urna. Cras vitae arcu ornare, vulputate diam nec, varius massa. Donec tincidunt maximus porttitor. Curabitur convallis lorem dui, vel mollis elit porttitor sed. Integer rhoncus, ipsum in semper lobortis, enim enim facilisis sapien, sed ultrices mauris augue in dolor.

                Nullam sed arcu quis elit vehicula fringilla nec non erat. Sed lacinia tristique orci sed finibus. Suspendisse tristique dolor nec lacinia lobortis. Nullam molestie dapibus nulla, at vehicula ante venenatis ut. Suspendisse interdum nunc nec arcu interdum gravida. Donec semper feugiat elementum. Sed fermentum nulla eros, a interdum nisl imperdiet quis.
                
                Fusce mi tortor, tempor vel elit sed, sagittis facilisis metus. Praesent consectetur consequat turpis, eu vulputate metus sodales sed. Aliquam interdum, ipsum ut facilisis pellentesque, lorem tortor euismod lectus, non venenatis libero lorem a elit. Donec tempor ligula vel nisi pretium, at pretium nisl condimentum. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin vel massa a mauris ornare porta eget a odio. Suspendisse nibh lacus, ultricies id tristique nec, venenatis non odio. Aliquam varius orci turpis, eu feugiat diam mattis sit amet. Maecenas a metus ultrices, finibus enim a, pulvinar enim. Proin est justo, semper eu magna id, aliquam dignissim purus. Maecenas in ultricies arcu. Etiam sollicitudin sit amet ligula in commodo. Integer nulla sapien, egestas at consequat ut, finibus in turpis. Vestibulum vitae ultrices ipsum. Duis pulvinar nec odio nec hendrerit. Nunc sed ultrices erat."""

if __name__ == "__main__":
    # file = "func/pdf/102-combinatorial-problems.pdf"
    file = "func/pdf/Quant guide (SBC).pdf"
    start, end = 5, 8
    print(get_summary(get_jumbled_text(file, start, end), "Formulas I need to know"))
