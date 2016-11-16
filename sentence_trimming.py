'''
Created on Nov 14, 2016
preprocessing of the positive and negative sentences

@author: rsong_admin
'''
from nltk.corpus import stopwords

import csv
import re
import pandas as pd
import numpy as np
import nltk
import string


def _remove_plural(sentence, product, reactant):
    '''
    use lancaster stemmer to remove tense and plural from a sentece
    '''
    st = nltk.PorterStemmer()
    sentence = sentence.split()
    sentence = " ".join(st.stem(word) for word in sentence)
    print sentence
    
def _replace_chem_name(sentence, product, reactant):
    '''
    function to handle the case when product or reactant is in one of the other
    e.g. product: sodium; reactant: sodium hydroxide
    
    also need to deal with the pluarl form of chemical names 
    '''
    
    product = product.strip()
    reactant = reactant.strip()
    
    # remove plural here
    
    if product not in reactant and reactant not in product:
        # if products and reactants are exclusive
        sentence = re.sub(product+'s?', 'CHEMICAL1', sentence)
        sentence = re.sub(reactant+'s?','CHEMICAL2', sentence)
    elif product in reactant:
        # order matters now
        sentence = re.sub(reactant+'s?', 'CHEMICAL1', sentence)
        sentence = re.sub(product+'s?','CHEMICAL2', sentence)
    elif reactant in product:
        # order matters 
        sentence = re.sub(product+'s?', 'CHEMICAL1', sentence)
        sentence = re.sub(reactant+'s?','CHEMICAL2', sentence)

    return sentence

def _tokenize_sentence(input_sentence, buffer=5):
    '''
    tokenize the sentence, with input buffer
    remove stop words and digits
    
    Also stem the tokenized sentence
    '''

    input_sentence = " ".join("".join([" " if ch in string.punctuation else ch for ch in input_sentence]).split()) # remove punctuation
    
    token_sentence = nltk.word_tokenize(input_sentence) # tokenize the sentence
     
    token_sentence = map(str, token_sentence) # convert each element to string
    
    ''' remove the stop words here '''
    token_sentence = [word for word in token_sentence if word not in stopwords.words('english')]
    
    ''' remove digits '''
    token_sentence = [word for word in token_sentence if not word.isdigit()]
    
    ''' trimming '''
    first_index = max(0, min(token_sentence.index("CHEMICAL1") - buffer, token_sentence.index("CHEMICAL2") - buffer)) # take the index of the first appearance of the product or reactant, whichever come first, minus the buffer
    last_index = min(len(token_sentence), max(token_sentence.index("CHEMICAL2") + buffer, token_sentence.index("CHEMICAL1") + buffer)) # the same logic as the one above
    
    token_sentence = token_sentence[first_index: last_index] # trimming here
    
    return token_sentence
    
def trim_sentence(df, buffer=5):
    '''
    this function trim the sentence to only get the words between each pair
    plus few words before and after each pair (depends on the buffer)
    '''
    trimmed_sentence = []
    for eachRow in df.iterrows():
        this_product = eachRow[1][0].strip()
        this_reactant = eachRow[1][1].strip()
        all_sentences = eachRow[1][2:]
        for eachSentence in all_sentences:
            if not pd.isnull(eachSentence): # check if a cell in pandas is not nan
                eachSentence = eachSentence.encode('ascii','ignore')

                # check if each sentence contains both the reactants and products
                if this_product in eachSentence and this_reactant in eachSentence:
                    
                    eachSentence = _replace_chem_name(eachSentence, this_product, this_reactant)
                    
                    eachSentence = _tokenize_sentence(eachSentence, buffer=5)
                    trimmed_sentence.append(eachSentence)
                else:
                    # if the sentence does not have both product and reactants
                    continue
            else:
                # break for null sentence, indicating the end of this line
                break
            
    return trimmed_sentence

if __name__ == '__main__':
    df = pd.read_excel('./data/positive_cleanup.xlsx',header=None)
    trimmed_sentence = trim_sentence(df)
    
    with open('trimmed_sentence.csv','wb') as myfile:
        thisWriter = csv.writer(myfile)
        for eachSentence in trimmed_sentence:

            thisWriter.writerow(eachSentence)
        
   

    

    
    
    
    
    