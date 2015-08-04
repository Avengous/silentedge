from LoLRequest import Request

class Match():
	def __init__(self, matchData):
		self.stats = matchData
	
	def kda(self):
		k = float(self.stats['kills'])
		d = float(self.stats['deaths'])
		a = float(self.stats['assists'])

		try:
			return round((k+a)/d, 2)
		except:
			return round(k+a, 2)

	#Need to call from a database or cache to improve performance.
	def champion(self):
		return Request().champions[self.stats['championId']]
		