import os
from human import Human
import mongoTools
class RnwMaker:
	def __init__(self, db, table, title="Data Party", author = "Christian Battista", human = ""):
		if human:
			self.human = human
		else:
			self.human = Human(db)
		self.title = title
		self.author = author
		self.name = title
		self.fname = self.name.replace(' ', '_')

		path = os.path.join("output", self.fname)
		 
		f = open("%s.Rnw" % path, "w")

		self.f = f
		self.lvl = 1


		self.WriteTitle()

	def WriteTitle(self):
		output = "\documentclass{article}\n\usepackage[utf8x]{inputenc}\n"
		output += "\\title{%s}\n\\author{%s}\n" % (self.title, self.author)
		output += "\\begin{document}\n\maketitle\n\\tableofcontents\n\\newpage\n"
		self.f.write(output)


	def AddText(self, text):
		self.f.write(str(text))

	def AddTextFile(self, textfile):
		f = open(textfile, r)
		lines = textfile.read()
		f.close()
		self.f.write(lines)

	def ChangeLevel(self, lvl):
		self.lvl = lvl

		
	def AddSection(self, factors, prefix = "Effect of"):
		lvl = self.lvl

		if lvl == 1:
			tag = "\section"
		else:
			self.lvl = lvl
			tag = "\%ssection" % ("sub" * (lvl-1)) 

		label = "%s %s" % (prefix, self.human.translate(factors))
		
		self.f.write("%s{%s}\n" % (tag, label))
		
	def AddAnalysis(self, factors, measure, datFile, caption="", hypothesize = False):
		lvl = self.lvl

		output = ""

		if lvl == 1:
			tag = "\section"
		else:
			tag = "\%ssection" % ("sub" * (lvl-1))

		



		output += "<<echo=false>>=\n"
		if len(factors) > 1:
			dfName = ""
			fName = ""
			for f in factors:
				dfName = dfName + "_" + f
				fName = fName + "*" + f
			dfName = dfName.lstrip("_")
			dfName = dfName + "_" + measure
			fName = fName.lstrip("*")
				
		else:
			dfName = factors[0] + "_" + measure
			fName = factors[0]		
		output += "%s = read.table(\"%s\", header=TRUE, sep=\",\")\n@\n" % (dfName, datFile)
		
		output += "%s{%s}\n" % (tag, self.human.translate(measure).title())
		if hypothesize:
			output += self.human.hypothesize(factors, measure)

		output += """<<>>==\n%sModel = aov(%s ~ (%s) + Error(s_id/(%s)), data=%s)\nsummary(%sModel)\n@\n""" % (measure, measure, fName, fName, dfName, measure)

		#if len(factors) > 1:
		#	pass
		#else:
		output += """\\begin{figure}\n\\begin{center}
<<echo=false,fig=true>>==\nboxplot(%s~%s,data=%s, ylab="%s", main="%s")\n@\n\end{center}\n\caption{%s}\n\end{figure}\n""" % (measure, fName, dfName, self.human.translate(measure),self.human.translate(fName), caption)
					
		self.f.write(output)
		
	def Close(self, execute=False):
		self.f.write("\end{document}\n")
		self.f.close()
		if execute:
			os.chdir(os.path.join(os.getcwd(), "output"))
			os.system("R CMD Sweave %s.Rnw" % self.fname)
			os.system("R CMD pdflatex %s.tex" % self.fname)
		del self.f
