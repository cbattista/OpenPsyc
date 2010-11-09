#counterbalance.py

"""
C. Battista CounterBalancing Module
Copyright (C) 2010 Christian Joseph Battista/Jobe Microsystems

email - battista.christian@gmail.com

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program, 'LICENSE.TXT'; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import pickle

class Counterbalance():
	def __init__(self, items, name = "cb.pck"):
		self.items = items
		self.name = name
		perms = self.all_perms(items)
		self.perms = []
		for item in perms:
			self.perms.append(item)

	def all_perms(self, items):
		if len(items) <=1:
		    yield items
		else:
		    for perm in self.all_perms(items[1:]):
		        for i in range(len(perm)+1):
		            yield perm[:i] + items[0:1] + perm[i:]

	def advance(self):
		current = self.perms.pop(0)
		self.perms.append(current)
		return current

	def save(self):
		f = open(self.name, "w")
		pickle.dump(self, f)
		f.close()
	

