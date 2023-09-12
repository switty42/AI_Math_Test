# ChatGPT Math Test
# Author Stephen Witty switty@level500.com
# 9-4-23
# Test ChatGPT math ability on simple problems
#
# Example code from rollbar.com - GPT example
#
# V1 9-4-23 - Initial release / dev
# V2 9-9-23 - Clean up comments
# V3 9-9-23 - Clean up more comments
# V4 9-12-23 - Add timeout to GPT
#
# Notes - Add your OpenAI key below

import openai
import time
import sys
import os
import random

# Put OpenAI API key here
openai.api_key = "XXXXXXXXXXXXXXXXXXXXX"

# Uncomment GPT model desired here
gpt_model='gpt-3.5-turbo'
#gpt_model = "gpt-4"

###################### Constants ##########################################################
NUMBER_OF_MATH_PROBLEMS = 30      # Number of problems before exiting
GPT_RETRY_LIMIT = 25              # Number of times to retry GPT if errors occur

########## This function creates the AI prompt #######
def create_gpt_prompt(math_problem):

   prompt_message = "What is the answer to this math problem? " + math_problem + \
"\nProvide back the answer inside of {}.  Provide the answer only.  For example if the answer is 7, then reply back with {7}"

   return prompt_message

########### This function formats an output string ####################
def print_string(string):
   cnt = 0
   for char in string:
      if not (char == " " and cnt == 0):
         print(char, end = "")
         cnt = cnt + 1
      if (cnt > 115 and char == " "):
         print()
         cnt = 0
   print()
   sys.stdout.flush()

############### Function - Call ChatGPT #########################################
def call_gpt(prompt_message):
   try:
      response = openai.ChatCompletion.create(model=gpt_model, messages=[ {"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt_message}],request_timeout=15)
   except Exception as e:
      return False, "", "WARNING:  System Error during ChatGPT call: " + str(e)

   return True, response.choices[0]["message"]["content"], ""

############## Create math problem ############################################
# Return math problem as string and answer
def create_problem():
   first = random.randrange(0,30) # Adjust ranges of numbers in problem here 
   second = random.randrange(0,30)
   third = random.randrange(0,30)
   problem_string = "(" + str(first) + " + " + str(second) + ")" + " * " + str(third) + " ="
   return (first + second) * third, problem_string

##################### Function - parse the space answer from GPT reply ############################
# Going to some lengths to verify the answer from GPT is a number since replies are often unpredictable
# Three return codes - Success True/False, answer, Error message if any
def parse_answer(message):
   global error_text
   cnt = 0
   cnt2 = 0
   pos = 0
   for char in message:
      if (char == "{"):
         cnt = cnt + 1
         start = pos
      if (char == "}"):
         cnt2 = cnt2 + 1
         end = pos
      pos = pos + 1

   if (cnt == 0 or cnt2 == 0):
      return False, 0, "WARNING: No brackets or incomplete"

   if (cnt > 1 or cnt2 > 1):
      return False, 0, "WARNING:  Too many brackets in output from GPT"

   if (end < start):
      return False, 0, "WARNING: Brackets are reversed in output from GPT"

   if ((end - start) > 10):
      return False, 0, "WARNING Too much space between brackets"

   if ((end - start) < 2):
      return False, 0, "WARNING Too few spaces between brackets" 

   string_number = ""
   for a in range (start + 1, end):
      if (message[a] == ","):
         continue
      if (message[a].isdigit()):
         string_number = string_number + message[a]
      else:
         return False, 0, "WARNING: Answer is not all digits"

   print("\nGPT string decoded: " + string_number)

   answer = int(string_number)

   return True, answer, ""

###############  Start of main routine ##############################################################
number_of_problems = 0

total_correct = 0
total_wrong = 0

# Store a history of wrong problems to display at the end of the program run
prob_hist_wrong = []
prob_hist_gpt_answer = []
prob_hist_actual_answer = []

while(number_of_problems < NUMBER_OF_MATH_PROBLEMS): # Main loop to start problems

   # Create math problem
   actual_answer, math_string = create_problem()

   # Create GPT prompt
   prompt = create_gpt_prompt(math_string)

   print("\n************************************** GPT Prompt ********************")
   print_string(prompt)

   ################### Call GPT and decode answer reply
   retry_count = 0
   success = False # Keep running prompt until we get a valid answer to check

   while (not success):

      if (retry_count == GPT_RETRY_LIMIT):
         print("\n\nERROR: Too many GPT errors, exiting\n")
         sys.exit()

      success, gpt_reply, error_text = call_gpt(prompt) # Call GPT, retry if error
      if (not success):
         print(error_text)
         retry_count = retry_count + 1
         continue

      print("\n*************** GPT Answer *****************")
      print_string(gpt_reply)

      success, gpt_answer, error_text = parse_answer(gpt_reply) # Decode GPT answer, retry if error
      if (not success):
         print(error_text)
         retry_count = retry_count + 1
         continue

   print("Actual answer " + str(actual_answer))

   if (actual_answer == gpt_answer):
      print("GPT is Correct")
      total_correct = total_correct + 1
   else:
      print("GPT is Wrong")
      total_wrong = total_wrong + 1
      prob_hist_wrong.append(math_string)
      prob_hist_gpt_answer.append(gpt_answer)
      prob_hist_actual_answer.append(actual_answer)

   print("Total correct: " + str(total_correct) + " Total wrong: " + str(total_wrong))

   number_of_problems = number_of_problems + 1

print("\n\n****** Final report *******************************************************************\n")
print("Total correct: " + str(total_correct) + " Total wrong: " + str(total_wrong))
print("\n******** Problems where GPT was incorrect *******\n")
for a in range(0,total_wrong):
   print("Problem: " + f"{prob_hist_wrong[a] : <18}" + "GPT answer: " + f"{prob_hist_gpt_answer[a] : <6}" + "Actual Answer: " + str(prob_hist_actual_answer[a]))
