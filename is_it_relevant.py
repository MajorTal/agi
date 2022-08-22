"""
Compare a question and a sentence from the passage.
"""
import os
# 3rd party imports:
import openai

openai.api_key = os.getenv("OPENAI_API_KEY") # I have an ".env" file


# Does it answer the question?
PROMPT = """
question: will there be a green lantern 2 movie
topic: Green Lantern (film)
sentence: Green Lantern was released on June 17, 2011, and received generally negative reviews; most criticized the film for its screenplay, inconsistent tone, choice and portrayal of villains, and its use of CGI, while some praised Reynolds' performance
relevant: NO

question: does the icc has jurisdiction in the united states
topic: United States and the International Criminal Court
sentence: The United States should have the chance to observe and assess the functioning of the court, over time, before choosing to become subject to its jurisdiction.
relevant: YES

question: calcium carbide cac2 is the raw material for the production of acetylene
topic: Calcium carbide
sentence: Calcium carbide is a chemical compound with the chemical formula of CaC
relevant: NO

question: is there a now you see me 3 coming out
topic: Now You See Me (film series)
sentence: Now You See Me is a series of heist thriller film written by Ed Solomon, Boaz Yakin, and Edward Ricourt.
relevant: NO

question: does a penalty shoot out goal count towards the golden boot
topic: Penalty shoot-out (association football)
sentence: A shoot-out is usually considered for statistical purposes to be separate from the match which preceded it.
relevant: NO

question: will there be a new season of cutthroat kitchen
topic: Cutthroat Kitchen
sentence: The show ended on its fifteenth season in July 2017.
relevant: YES

question: is jack sikma in the hall of fame
topic: Jack Sikma
sentence: Inducted alongside Sikma were Zelmo Beaty, Walt Frazier, Bob Love, Elmore Smith, Jim Spivey, Rico Swanson, George Tinsley, and Al Tucker.'
relevant: NO

question: can elves and humans mate lord of the rings
topic: Half-elven
sentence: In J.R.R. Tolkien's fictional universe of Middle-earth, the Half-elven (Sindarin singular Peredhel, plural Peredhil, Quenya singular Perelda) are the children of the union of Elves and Men
relevant: YES

question: the boy in the plastic bubble based on true story
topic: The Boy in the Plastic Bubble
sentence: The Boy in the Plastic Bubble is a 1976 American made-for-television drama film inspired by the lives of David Vetter and Ted DeVita, who lacked effective immune systems.
relevant: YES

question: is tim brown in the hall of fame
topic: Tim Brown (American football)
sentence: Brown has also played for the Tampa Bay Buccaneers.
relevant: NO

question: can you drink alcohol in public in denmark
topic: Drinking in public
sentence: Drinking in public in Denmark is legal in general.
relevant: YES

question: is jersey currency legal tender in the uk
topic: Jersey pound
sentence: Both Jersey and Bank of England notes are legal tender in Jersey and circulate together, alongside the Guernsey pound and Scottish banknotes.
relevant: NO

question: {}
topic: {}
sentence: {}
relevant: """

def predict(question, topic, sentence):
    prompt = PROMPT.format(question, topic, sentence)
    res = openai.Completion.create(
                model="text-davinci-002",
                prompt=prompt,
                temperature=0.3,
                stop = ["question", "topic", "sentence", "relevant"],
                # n = 3
            )
    print(res)
    reply = res["choices"][0]["text"].strip().lower() == "y"
    return reply


if __name__ == "__main__":
    RES = predict(
        question="is kingdom manga based on a true story",
        topic = "Kingdom (manga)",
        sentence = "Kingdom (キングダム, Kingudamu) is a Japanese manga series written and illustrated by Yasuhisa Hara (原泰久, Hara Yasuhisa).")
    print(RES, type(RES))