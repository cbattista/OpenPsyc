import os
from statistician import Statistician
import mongoTools
import statistician

class RnwMaker:
	def __init__(self, db, table, title="Data Party", author = "Christian Battista", human = ""):
		if human:
			self.human = human
		else:
			self.human = Statistician(db)

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

	def addFigure(self, figure, caption=""):
		output = """\\begin{figure}\n\\begin{center}\n<<echo=false,fig=true>>==\n%s\n@\n\end{center}\n\caption{%s}\n\end{figure}\n""" % (figure, caption)
		return output


	def compareMeans(self, factors, measure, datFile, caption="", interpret = False):
		output, dfName = self.AddAnalysis(factors, measure, datFile)

		model = "%s~%s+Error(s_id/%s)" % (measure, fName, fName)
		output += "%s{%s}\n" % (tag, self.human.translate(measure).title())
		
		if interpret:
			output += self.human.interpret(factors, measure, model, datFile)

		caption += ".  %s" % self.human.hypothesize(factors, measure)

		output += """<<>>==\n%sModel = aov(%s, data=%s)\nsummary(%sModel)\n@\n""" % (measure, model, dfName, measure)

		figure = """boxplot(%s~%s,data=%s, ylab="%s", main="%s")""" % (measure, fName, dfName, self.human.translate(measure),self.human.translate(fName))
		output += self.addFigure(figure, caption)

		self.f.write(output)		

	def correlate(self, factors, measure, datFile, caption=""):	
		output, dfName, factors = self.AddAnalysis(factors, measure, datFile)

		sig, r, p = self.human.correlate(measure[0], measure[1], datFile)

		output += "\nr=%2.2f, p<%0.2f\n\n" % (r, p)

		if not factors:

			figure = "plot(%s$%s, %s$%s, xlab = \"%s\", ylab = \"%s\")" % (dfName, measure[0], dfName, measure[1], self.human.translate(measure[0]), self.human.translate(measure[1]))
			
			output += self.addFigure(figure, caption)	

		else:
			for f in factors:
				output += self.addFigure("scatterplot(%s ~ %s | %s, data=%s)" % (measure[0], measure[1], f, dfName), caption)


		self.f.write(output)


	def AddAnalysis(self, factors, measure, datFile):
		if type(factors) == str:
			factors = [factors]

		lvl = self.lvl

		dfName = ""
		fName = ""

		output = ""

		if lvl == 1:
			tag = "\section"
		else:
			tag = "\%ssection" % ("sub" * (lvl-1))

		output += "<<echo=false>>=\n"
		output += "library(car)\n"
		for f in factors:
			dfName = dfName + "_" + f
			fName = fName + "*" + f
		dfName = dfName.lstrip("_")
		fName = fName.lstrip("*")
				
		if type(measure) == list:
			m = ""
			for meas in measure:
				m+= "_%s" % meas
			dfName += m
		else:
			dfName+= "_%s" % measure

		dfName = dfName.lstrip("_")
				
		output += "%s = read.table(\"%s\", header=TRUE, sep=\",\")\n@\n" % (dfName, datFile)

		return output, dfName, factors
		
	def Close(self, execute=False):
		self.f.write("\end{document}\n")
		self.f.close()
		if execute:
			os.chdir(os.path.join(os.getcwd(), "output"))
			os.system("R CMD Sweave %s.Rnw" % self.fname)
			os.system("R CMD pdflatex %s.tex" % self.fname)
		del self.f
