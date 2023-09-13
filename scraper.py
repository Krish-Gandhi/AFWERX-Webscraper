from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import transformers
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
from IPython.display import display
import pandas as pd
import numpy as np

solutions = []
short = []

#used to scrape the page
#takes in Selenium driver, login and url numbers of the page
def scrape_page(driver, username, password, urlNum, start):
    
    #initializes a list to store scraped data
    data=[]
    
    try:
        #gets current page
        url = "https://afwerxchallenge.com/uaspower/uas-power-challenge_265/solutionsubmissionphase/suggestion/"+str(urlNum)
        driver.get(url)
        driver.implicitly_wait(10)
        
        #the AFWERX page will ask for a login on the first time,
        #because, if selected, the submission ideas/products
        #could be utilized by the US Air Force
        if (urlNum < start + 1):
            driver.find_element("id","email").send_keys(username)
            driver.find_element("id","email").send_keys(Keys.ENTER)

            driver.implicitly_wait(10)
            driver.find_element("id","password").send_keys(password)
            driver.find_element("id","password").send_keys(Keys.ENTER)
        
        driver.implicitly_wait(10)
        
        #makes sure page is actually loaded and not asking for login
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element(By.TAG_NAME, "h1").text != "Enter password"
        )

        #AFWERX Challenges run multiple challenges
        #if the page's submission is in the correct challenge,
        #the webscraping will begin
        challenge = driver.find_element(By.TAG_NAME, "h1")        
        if challenge.text == "UAS Power Generation Challenge":
            page = driver.find_element(By.TAG_NAME, "frontend-root").find_element(By.TAG_NAME, "fe-tab-content")
            driver.implicitly_wait(10)
            
            #starts populating data list
            title = page.find_element(By.TAG_NAME, "h1").text
            
            if title.lower() != "Test".lower():
            
                info = page.find_elements(By.TAG_NAME, "dynamic-content")

                for a in range(len(info)):
                    info[a] = info[a].text
                #print(info)

                maturity = page.find_elements(By.TAG_NAME, "p")
                for a in range(len(maturity)):
                    maturity[a] = maturity[a].text
                #print(maturity)


                focusAreas = page.find_elements(By.TAG_NAME, "span")[1:]
                for a in range(len(focusAreas)):
                    focusAreas[a] = focusAreas[a].text

                att = driver.find_element(By.TAG_NAME, "frontend-root").find_element(By.TAG_NAME, "fe-suggestion-infobar").find_elements(By.TAG_NAME, "span")
                for a in range(len(att)):
                    att[a] = att[a].text

                for a in att:
                    try:
                        focusAreas.remove(a)
                    except:
                        print(end="")
                #print(focusAreas)

                data.append("___COMPANY___")
                data.append(maturity[-3])
                data.append(maturity[-2])
                data.append(maturity[-1])
                data.append("___PRODUCT___")
                data.append(title)
                data.append(info[0])
                data.append(info[1])
                data.append(focusAreas)
                data.append(info[2])
                data.append(info[3])
                data.append(maturity[-6])
                data.append(info[4])
                data.append(maturity[-4])
                for i in range(5, len(info)):
                    data.append(info[i])

                data.append(url)
                
                #
                solutions.append(data)
    except:
            print("Error on", urlNum)
    
def scrape_solutions():
    driver = webdriver.Chrome()
    
    #Scrapes all the submitted solutions
    #iterate holds all the URL numbers that need to be scraped
    iterate = [14339, 14340, 14349, 14351, 14353]
    
    for i in iterate:
        scrape_page(driver, USERNAMEGOESHERE, PASSWORDGOESHERE, i, iterate[0])
        
    driver.quit() 

#this function is used to summarize the entries in solutions
def summarize():
    i=0
    for a in solutions:
        i+=1
        shorter = []
        
        # if the title is longer than 25 characters, summarize it
        if (len(a[5]) < 25):
            shorter.append(a[5])
        else:
            shorter.append(summarize_paragraph(a[5]))
        
        # if the overview is longer than 50 characters, summarize it
        if (len(a[6]) < 50):
            shorter.append(a[6])
        else:
            shorter.append(summarize_paragraph(a[6]))
          
        short.append(shorter)
        print("Summarized",i,"of",len(solutions),"...")

        
#i have no idea how this works
def summarize_paragraph(input_text):
    # Load the T5 base model and its tokenizer.
    t5_model = T5ForConditionalGeneration.from_pretrained('t5-large')
    t5_tokenizer = T5Tokenizer.from_pretrained('t5-large')

    preprocess_text = input_text.strip().replace("\n", "")
 
    # Add T5 prefix for text summarization
    t5_ready_text = "summarize: " + preprocess_text
    device = torch.device('cpu')

    # Tokenize input text
    tokenized_text = t5_tokenizer.encode(t5_ready_text, return_tensors = "pt").to(device)
    tokenized_text
    summary_tokens = t5_model.generate(tokenized_text,
                                  num_beams = 4,
                                  no_repeat_ngram_size = 2,
                                  min_length = 30,
                                  max_length = 100,
                                  early_stopping = True)
 
    summary_tokens
    t5_summary_output_text = t5_tokenizer.decode(summary_tokens[0], skip_special_tokens = True)

    return t5_summary_output_text

#this function is used to convert the lists into Excel 
def output():
    
    #takes the transpose of the arrays of the solutions
    #to make it easier to translate into Excel
    tpose = np.array(solutions).T
    tpose = tpose.tolist()
    tposeSUM = np.array(short).T.tolist()
    
    #Turns the focus areas from a list to a string
    for a in range(len(tpose[8])):
        temp = ""
        for b in tpose[8][a]:
            temp += b
            temp += '\n'
        tpose[8][a] = temp
    
    #defines the dictionary for summary excel sheet
    shorter = {
        "Company" : tpose[0],
        "Reference ID" : tpose[1],
        "Submission Date" : tpose[2],
        "Status" : tpose[3],
        "Product" : tpose[4],
        "Title Summary" : tposeSUM[0],
        "Overview Summary" : tposeSUM[1],
        "Focus Areas" : tpose[8],
        "Solution Maturity" : tpose[11],
        "Keywords Related" : tpose[14],
        "Timeline to Implementation" : tpose[13],
        "Point of Contact" : tpose[15],
        "Point of Contact Email" : tpose[16],
        "Link" : tpose[19]
        }
    
    #defines the dictionary for non-summary excel sheet
    full = {
        "Company" : tpose[0],
        "Reference ID" : tpose[1],
        "Submission Date" : tpose[2],
        "Status" : tpose[3],
        "Product" : tpose[4],
        "Title" : tpose[5],
        "Overview" : tpose[6],
        "Solution Description" : tpose[7],
        "Focus Areas" : tpose[8],
        "Value Proposition to USAF" : tpose[9],
        "Inputs/Outputs" : tpose[10],
        "Solution Maturity" : tpose[11],
        "Can Proof of Concept be provided prior to implentation to scale?" : tpose[12], 
        "Keywords Related" : tpose[14],
        "Timeline to Implementation" : tpose[13],
        "Point of Contact" : tpose[15],
        "Point of Contact Email" : tpose[16],
        "Point of Contact Phone" : tpose[17],
        "Point of Contact Address" : tpose[18],
        "Link" : tpose[19]
    }
    
    #uses pandas to build summary Excel sheet
    df = pd.DataFrame(shorter)    
    df.to_excel("SUMMARY SHEET.xlsx")
    display(df)
    
    #uses pandas to build non-summary Excel sheet
    dfF = pd.DataFrame(full)    
    dfF.to_excel("FULL SHEET.xlsx")
    display(dfF)

    
    
#actually runs the code
scrape_solutions()
print("Summary Start")
summarize()
print("Summary Done")
output()