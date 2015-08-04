import LoL
from LoLReport import Report

for player in LoL.PLAYERIDS:
	print "Creating report for {}...".format(player)
	Report(player).create()