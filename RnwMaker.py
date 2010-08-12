from human import HumanReadable
import os

class RnwMaker:
	def __init__(self, db, table, title="Data Party", author = "Christian Battista"):
		self.title = title
		self.author = author
		self.name = "%s_%s" % (db, table)
		path = os.path.join("output", self.name)
		self.f = open("%s.Rnw" % path, 'w')
		self.WriteTitle()
		
	def WriteTitle(self):
		output = "\documentclass{article}\n\usepackage[utf8x]{inputenc}\n"
		output += "\\title{%s}\n\\author{%s}\n" % (self.title, self.author)
		output += "\\begin{document}\n\maketitle\n\\tableofcontents\n\\newpage\n"
		self.f.write(output)

	def AddText(self, textfile):
		f = open(textfile, r)
		lines = textfile.read()
		f.close()
		self.f.write(lines)
		
	def AddSection(self, factors):
		if len(factors) > 1:
			aName = ""
			for f in factors:
				aName = "%s and %s" % (aName, f)
				aName = aName.lstrip(" and")
		else:
			aName = factors[0]

		self.f.write("\section{Effect of %s}\n" % HumanReadable(aName))
		
	def AddAnalysis(self, factors, measure, datFile):
		output = "<<echo=false>>=\n"
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
		
		output += "\subsection{%s}\n" % HumanReadable(measure)
		
		output += """<<>>==\n%sModel = aov(avg ~ (%s) + Error(s_id/(%s)), data=%s)\nsummary(%sModel)\n@\n""" % (measure, fName, fName, dfName, measure)

		if len(factors) > 1:
			pass
		else:
			output += """\\begin{figure}\n\\begin{center}
<<echo=false,fig=true>>==\nboxplot(avg~%s,data=%s, ylab="%s", main="%s")\n@\n\end{center}\n\caption{}\n\end{figure}\n""" % (fName, dfName, HumanReadable(measure),HumanReadable(fName))
					
		self.f.write(output)
		
	def Close(self, execute=False):
		self.f.write("\end{document}\n")
		self.f.close()
		if execute:
			os.chdir(os.path.join(os.getcwd(), "output"))
			os.system("R CMD Sweave %s.Rnw" % self.name)
			os.system("R CMD pdflatex %s.tex" % self.name)
