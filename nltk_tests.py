#################################################################
# File Name: nltk_main.py					#
# Date Created: 06-16-2015					#
# Date Revised: 06-16-2015					#
# Author: Benjamin S. Meyers					#
# Email: bsm9339@rit.edu					#
# 	Advisor: Emily Prud'hommeaux				#
# 	Email: emilypx@rit.edu					#
# 	Advisor: Cissi Ovesdotter-Alm				#
# 	Email: coagla@rit.edu					#
#################################################################
from nltk_functions import *

##### TEST FUNCTIONS ############################################
def check_tokenize_accuracy():
	if get_tokens('moby_dick.txt') == get_tokens('moby_dick.txt'):
		return 'PASSED!'
	else:
		return 'FAILED!'

def run_tests():
	print('##### RUNNING TESTS #############################################')
	print('\nget_tokens(str) status: ' + check_tokenize_accuracy())
	print('\n#################################################################')
