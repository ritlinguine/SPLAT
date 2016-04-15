#!/usr/bin/python3.4

##### PYTHON IMPORTS ###################################################################################################
import os.path, sys, re

##### SPLAT IMPORTS ####################################################################################################
from splat.model.FullNGramminator import FullNGramminator
from splat.parse.TreeStringParser import TreeStringParser
from splat.sentenizers.CleanSentenizer import CleanSentenizer
from splat.tag.NLTKPOSTagger import NLTKPOSTagger
from splat.tokenizers.RawTokenizer import RawTokenizer
from splat.tokenizers.CleanTokenizer import CleanTokenizer
from splat.annotation.MeyersDialogActAnnotator import MeyersDialogActAnnotator
from splat.annotation.SpeakerIndicatorAnnotator import SpeakerIndicatorAnnotator
import splat.base.Util as Util
import splat.complexity.Util as cUtil

########################################################################################################################
##### INFORMATION ######################################################################################################
### @PROJECT_NAME:		SPLAT: Speech Processing and Linguistic Annotation Tool										 ###
### @VERSION_NUMBER:																								 ###
### @PROJECT_SITE:		github.com/meyersbs/SPLAT																     ###
### @AUTHOR_NAME:		Benjamin S. Meyers																			 ###
### @CONTACT_EMAIL:		ben@splat-library.org																		 ###
### @LICENSE_TYPE:																									 ###
########################################################################################################################
########################################################################################################################

class TextBubble:
	"""
	A TextBubble is a bubble of text. It can be a single word, a paragraph, or even a whole novel!
	The TextBubble object makes it super simple to extract features from a selection of text.
	"""
	# Variable Declarations
	__wordcount, __unique_wordcount, __sentcount, __uttcount, __maxdepth = (0,) * 5
	__cfr, __alu, __ttr, __als, __cdensity, __idensity, __yngve_score, __frazier_score, __string_yngve, __string_frazier = (0.0,) * 10
	__sentences, __utterances, __rawtokens, __tokens, __pos, __treestrings = ([],) * 6
	__c_words, __f_words, __uc_words, __uf_words, __longest_words, shortest_words = ([],) * 6
	__rawtypes, __types, __poscounts, __dpu, __dps, __disfluencies, __annotated_utts, __syllables = ({},) * 8
	__bubble = ""
	__annotated_bubble, __freq_dist, __dpa, __flesch, __kincaid = (None,) * 5

	# Object Declarations
	__ngramminator = FullNGramminator()
	__cleantokenizer = CleanTokenizer()
	__rawtokenizer = RawTokenizer()
	__sentenizer = CleanSentenizer()
	__postagger = NLTKPOSTagger()
	__treestring_gen = TreeStringParser()
	__meyers_annotator = MeyersDialogActAnnotator()
	__speaker_annotator = SpeakerIndicatorAnnotator()

	def __init__(self, text, ngramminator=FullNGramminator(), postagger=NLTKPOSTagger()):
		"""
		Creates a TextBubble Object.
		"""
		if os.path.exists(text):
			temp_text, temp_annotated_text = ("",) * 2
			temp_utts = []
			temp_annotated_utts = {}
			for line in open(text, 'r'):
				if "(" in line:
					temp_annotated_text += line.strip() + " "
					split_line = line.strip("\n").strip(")").strip().split("(")
					utt_key = split_line[0].strip()
					temp_text += utt_key + " "
					temp_utts.append(utt_key.strip())
					utt_acts = split_line[1].strip().split(", ")
					temp_annotated_utts[utt_key] = utt_acts
				else:
					temp_utts.append(line.strip())
					temp_text += line.strip() + " "
			self.__bubble = temp_text
			self.__utterances = temp_utts
			self.__annotated_bubble = temp_annotated_text
			self.__annotated_utts.update(temp_annotated_utts)
		elif type(text) == str:
			self.__bubble = text
			temp_utts = []
			for line in text.split("\n"):
				temp_utts.append(line.strip())
			self.__utterances = temp_utts
		else:
			raise ValueError("WARNING: TextBubble must be of type str or file.")

		self.__uttcount = len(self.__utterances)
		self.__sentences = self.__sentenizer.sentenize(self.__bubble)
		if self.__sentences == []: self.__sentences = self.__utterances
		self.__sentcount = len(self.__sentences)
		self.__rawtokens = self.__rawtokenizer.tokenize(self.__bubble)
		self.__tokens = self.__cleantokenizer.tokenize(self.__bubble)
		self.__syllables = cUtil.count_syllables(self.__tokens)
		self.__longest_words = set([word for word in self.__tokens if len(word) == max(len(word) for word in self.__tokens)])
		self.__shortest_words = set([word for word in self.__tokens if len(word) == min(len(word) for word in self.__tokens)])
		self.__rawtypes = Util.typify(self.__rawtokens)
		self.__types = Util.typify(self.__tokens)
		self.__wordcount = Util.wordcount(self.__rawtokens)
		self.__unique_wordcount = Util.wordcount(self.__types)
		self.__ngramminator = ngramminator
		self.__postagger = postagger
		self.__ttr = Util.type_token_ratio(self.__types, self.__tokens)
		self.__pos = self.__postagger.tag(self.__bubble)
		self.__alu = round(float(self.__wordcount) / float(self.__uttcount), 4) if self.__uttcount != 0 else 0.0
		self.__als = round(float(self.__wordcount) / float(self.__sentcount), 4) if self.__sentcount != 0 else 0.0
		self.__c_words = Util.get_content_words(self.__tokens)
		self.__f_words = Util.get_function_words(self.__tokens)
		self.__uc_words = Util.get_unique_content_words(self.__types)
		self.__uf_words = Util.get_unique_function_words(self.__types)
		self.__cfr = Util.get_content_function_ratio(self.__tokens)
		self.__treestring_gen = TreeStringParser()
		self.__treestrings, self.__maxdepth, self.__yngve_score, self.__frazier_score, self.__string_yngve, self.__annotated_bubble, self.__dpa = (None,) * 7
		self.__cdensity = cUtil.calc_content_density(self.__pos)
		self.__idensity = cUtil.calc_idea_density(self.__pos)
		self.__poscounts = Util.get_pos_counts(self.__pos)
		self.__freq_dist = Util.get_freq_dist(self.__tokens)
		self.__dpu = Util.count_disfluencies(self.__utterances)
		self.__dps = Util.count_disfluencies(self.__sentences)
		self.__disfluencies = Util.total_disfluencies(self.__dpu)

	def bubble(self):
		""" Returns the raw TextBubble. """
		return self.__bubble

	def annotated_bubble(self):
		""" Returns the annotated TextBubble. """
		if self.__annotated_bubble is None:
			self.__meyers_annotator = MeyersDialogActAnnotator()
			temp_bubble = self.__meyers_annotator.annotate(self.__utterances)
			self.__speaker_annotator = SpeakerIndicatorAnnotator()
			self.__annotated_bubble = self.__speaker_annotator.annotate(temp_bubble)
			return self.__annotated_bubble
		else:
			return self.__annotated_bubble

	def annotated_utts(self):
		return self.__annotated_utts

	def disfluencies_per_act(self):
		"""
		If the User has not annotated the TextBubble, give a warning message.
		Otherwise, print out the disfluency statistics per dialog act.
		"""
		if self.__annotated_bubble is None:
			sys.exit("WARNING: No annotations are present. Try 'splat annotate <filename>'.")
		if self.__dpa is None:
			self.__dpa = Util.get_disfluencies_per_act(self.__annotated_bubble)
		template = "{0:7}{1:7}{2:7}{3:7}{4:7}{5:7}{6:7}{7:7}{8:100}"
		print(template.format("UM", "UH", "AH", "ER", "HM", "Pauses", "Reps", "Breaks", "Dialog Act"))
		for (k, v) in self.__dpa.items():
			print(template.format(str(v[0]), str(v[1]), str(v[2]), str(v[3]), str(v[4]), str(v[5]), str(v[6]), str(v[7]), k))
		return ''

	def syllables(self):
		""" Returns the number of syllables in the TextBubble. """
		return self.__syllables

	def flesch_readability(self):
		""" Returns the flesch readability score. """
		if self.__flesch is None:
			self.__flesch = cUtil.calc_flesch_readability(self.__wordcount, self.__sentcount, self.__syllables)
			return self.__flesch
		else:
			return self.__flesch

	def kincaid_grade_level(self):
		""" Returns the flesch-kincaid grade level score. """
		if self.__kincaid is None:
			self.__kincaid = cUtil.calc_flesch_kincaid(self.__wordcount, self.__sentcount, self.__syllables)
			return self.__kincaid
		else:
			return self.__kincaid

	def sents(self):
		""" Returns a list of all sentences contained within the TextBubble. """
		return self.__sentences

	def utts(self):
		""" Returns a list of all utterances contained within the TextBubble. """
		return self.__utterances

	def rawtokens(self):
		""" Returns a list of unnormalized tokens. """
		return self.__rawtokens

	def tokens(self):
		""" Returns a list of normalized tokens. """
		return self.__tokens

	def rawtypes(self):
		""" Returns a list of unnormalized types. """
		return self.__rawtypes

	def types(self):
		""" Returns a list of normalized types. """
		return self.__types

	def wordcount(self):
		""" Returns the total word (token) count. """
		return self.__wordcount

	def unique_wordcount(self):
		""" Returns the unique word (type) count. """
		return self.__unique_wordcount

	def sentcount(self):
		""" Returns the total sentence count. """
		return self.__sentcount

	def uttcount(self):
		""" Returns the total utterance count. """
		return self.__uttcount

	def type_token_ratio(self):
		""" Returns the ratio of types to tokens. """
		return self.__ttr

	def unigrams(self):
		""" Returns a list of unigrams. """
		return self.__ngramminator.unigrams(self.__bubble)

	def bigrams(self):
		""" Returns a list of bigrams. """
		return self.__ngramminator.bigrams(self.__bubble)

	def trigrams(self):
		""" Returns a list of trigrams. """
		return self.__ngramminator.trigrams(self.__bubble)

	def ngrams(self, n):
		""" Returns a list of n-grams.
		:param n: the size of the n-grams to be generated
		"""
		return self.__ngramminator.ngrams(self.__bubble, n)

	def pos(self):
		""" Returns a list of tuple pairs: (word, POS tag). """
		return self.__pos

	def average_utterance_length(self):
		""" Returns the average utterance length. """
		return self.__alu

	def average_sentence_length(self):
		""" Returns the average sentence length. """
		return self.__als

	def content_function_ratio(self):
		""" Returns the ratio of content words to function words. """
		return self.__cfr

	def content_words(self):
		""" Returns a list of content words. """
		return self.__c_words

	def function_words(self):
		""" Returns a list of function words. """
		return self.__f_words

	def unique_content_words(self):
		""" Returns a list of unique content words. """
		return self.__uc_words

	def unique_function_words(self):
		""" Returns a list of unique function words. """
		return self.__uf_words

	def treestrings(self):
		""" Returns a list of parse trees. """
		if self.__treestrings is None:
			self.__treestring_gen = TreeStringParser()
			self.__treestrings = self.__treestring_gen.get_parse_trees(self.__utterances)
		return self.__treestrings

	def drawtrees(self):
		""" Uses matplotlib and nltk to draw syntactic parse trees. """
		if self.__treestrings is None:
			self.__treestring_gen = TreeStringParser()
			self.__treestrings = self.__treestring_gen.get_parse_trees(self.__utterances)
		Util.draw_trees(self.__treestrings)
		return ''

	def words_per_utterance(self):
		""" Prints the number of words in each utterance. """
		for item in self.__utterances:
			print(len(item.split(" ")))
		return ''

	def words_per_sentence(self):
		""" Prints the number of words in each sentence. """
		for item in self.__sentences:
			print(len(item.split(" ")))
		return ''

	def longest_words(self):
		""" Returns the longest words in the text."""
		return self.__longest_words

	def shortest_words(self):
		""" Returns the shortest words in the text."""
		return self.__shortest_words

	def content_density(self):
		"""
		Returns the Content Density.
		Content Density is the ratio of open class words to closed class words.
		"""
		return self.__cdensity

	def idea_density(self):
		"""
		Returns the Idea Density.
		Idea Density is the ratio of propositions to total word count.
		"""
		return self.__idensity

	def tree_based_yngve_score(self):
		"""
		Returns the mean Yngve Score.
		Yngve score is... http://www.m-mitchell.com/papers/RoarkEtAl-07-SynplexityforMCI.pdf
		"""
		if self.__yngve_score is None:
			trees = []
			for treestring in self.treestrings():
				trees.append(treestring)
			return cUtil.get_mean_yngve(trees)
		else:
			return self.__yngve_score

	def string_based_yngve_score(self):
		"""
		Returns the mean Yngve Score.
		Yngve score is... http://www.m-mitchell.com/papers/RoarkEtAl-07-SynplexityforMCI.pdf
		"""
		print("WARNING: String-Based Yngve Score calculation is under review, and thus not available at this time.")
		if self.__string_yngve is None:
			trees = []
			for treestring in self.treestrings():
				trees.append(treestring)
			return cUtil.get_total_mean_yngve(trees)
		else:
			return self.__string_yngve

	def tree_based_frazier_score(self):
		"""
		Returns the Frazier Score.
		Frazier score is... http://www.m-mitchell.com/papers/RoarkEtAl-07-SynplexityforMCI.pdf
		"""
		if self.__frazier_score is None:
			trees = []
			for treestring in self.treestrings():
				trees.append(treestring)
			return cUtil.get_frazier_score(trees)
		else:
			return self.__frazier_score

	def string_based_frazier_score(self):
		"""
		Returns the Frazier Score.
		Frazier score is... http://www.m-mitchell.com/papers/RoarkEtAl-07-SynplexityforMCI.pdf
		"""
		print("WARNING: String-Based Frazier Score calculation is under review, and thus not available at this time.")
		return ''

	def pos_counts(self):
		""" Returns a dictionary with POS tags as keys and their frequencies as values. """
		return self.__poscounts

	def max_depth(self):
		""" Returns the maxdepth of all syntactic parse trees. """
		if self.__treestrings is None:
			self.__treestring_gen = TreeStringParser()
			self.__treestrings = self.__treestring_gen.get_parse_trees(self.__utterances)
		if self.__maxdepth is None:
			self.__maxdepth = Util.get_max_depth(self.__treestrings)
		return self.__maxdepth

	def get_most_freq(self, x=None):
		"""
		Returns the x most frequent words with their frequencies,
		or all words with their frequencies if x is not specified.
		:param x: the number of most frequent words to return
		"""
		if x is None:
			return self.__freq_dist.most_common()
		elif x > 0:
			return self.__freq_dist.most_common(x)
		else:
			return self.__freq_dist.most_common()

	def get_least_freq(self, x=None):
		"""
		Returns the x least frequent words with their frequencies,
		or all words with their frequencies if x is not specified.
		:param x: the number of least frequent words to return
		"""
		most_common = self.__freq_dist.most_common()
		freq_dist = []
		count = 0

		if x is None:
			freq_dist = most_common
		else:
			for item in reversed(most_common):
				if count < int(x):
					freq_dist.append(item)
					count += 1

		return freq_dist

	def plot_freq(self, x=None):
		""" Uses matplotlib to graph the frequency distribution.
		:param x:
		"""
		Util.plot_freq_dist(self.__freq_dist,x)
		return ''

	def disfluencies_per_utterance(self):
		""" Displays the number of each type of disfluency per each utterance. """
		template = "{0:7}{1:7}{2:7}{3:7}{4:7}{5:7}{6:7}{7:7}{8:7}{9:50}"
		print(template.format("UM", "UH", "AH", "ER", "HM", "Pauses", "Reps", "Breaks", "Words", "Text"))
		for (k, v) in self.__dpu.items():
			print(template.format(str(v[0]), str(v[1]), str(v[2]), str(v[3]), str(v[4]), str(v[5]), str(v[6]), str(v[7]), str(v[8]), k))

		return ''

	def dpu(self):
		""" Return the raw disfluencies per utterance dictionary. """
		return self.__dpu

	def disfluencies_per_sentence(self):
		""" Displays the number of each type of disfluency per each sentence. """
		template = "{0:7}{1:7}{2:7}{3:7}{4:7}{5:7}{6:7}{7:7}{8:7}{9:50}"
		print(template.format("UM", "UH", "AH", "ER", "HM", "Pauses", "Reps", "Breaks", "Words", "Text"))
		for (k, v) in self.__dps.items():
			print(template.format(str(v[0]), str(v[1]), str(v[2]), str(v[3]), str(v[4]), str(v[5]), str(v[6]), str(v[7]), str(v[8]), k))

		return ''

	def disfluencies(self):
		""" Displays the total number of each type of disfluency. """
		d = self.__disfluencies
		print("Nasal\tUM\tHM\tNon-Nasal\tUH\tAH\tER\tSilent Pauses\tRepetitions\tBreaks")
		print(str(d["Nasal"]) + "\t" + str(d["UM"]) + "\t" + str(d["HM"]) + "\t" + str(d["Non-Nasal"]) +
			  "\t\t" + str(d["UH"]) + "\t" + str(d["AH"]) + "\t" + str(d["ER"]) + "\t" + str(d["Pause"]) +
			  "\t\t" + str(d["Repetitions"]) + "\t\t" + str(d["Break"]))

		return ''

	def dis(self):
		""" Return the raw disfluencies dictionary. """
		return self.__disfluencies

	def splat(self):
		"""
		:return:a massive SPLAT of the different features in the TextBubble
		:rtype:str
		"""
		output = "===== Bubble:\n"
		output += self.__bubble + "\n"
		output += "===== Sentences:\n"
		count = 0
		for sentence in self.__sentences:
			output += "[" + str(count) + "] " + str(sentence) + "\n"
			count += 1
		output += "Sentence Count: " + str(self.__sentcount) + "\n"
		output += "===== Tokens:\n"
		output += str(self.__tokens) + "\n"
		output += "Word Count: " + str(self.__wordcount) + "\n"
		output += "===== Types:\n"
		output += str(self.__types) + "\n"
		output += "Unique Word Count: " + str(self.__unique_wordcount) + "\n"
		output += "===== Type-Token Ratio:\n"
		output += str(self.__ttr) + "\n"

		return output