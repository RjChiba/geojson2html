# -*- encoding utf-8 -*-

import sys, os
import traceback

#=== NOTICE ===========================================================
#
# The geographical data of Japan was kindly provided by japonyol.net
# https://japonyol.net/editor/article/47-prefectures-geojson.html
# 
#======================================================================

class Path:
	def __init__(self, position, viewbox):
		self.path = position
		self.box = viewbox

class Viewbox:
	def __init__(self, top=0, bottom=float('inf'), left=float('inf'), right=0):
		self.pos_top = top
		self.pos_bottom = bottom
		self.pos_left = left
		self.pos_right = right

	def shape(self):
		return [
			self.pos_left, self.pos_bottom, self.pos_right - self.pos_left, self.pos_top - self.pos_bottom
		]

def updateViewbox(box1, box2):

	if type(box1) == Viewbox and type(box2) == Viewbox:
		posT = max(box1.pos_top    , box2.pos_top)
		posB = min(box1.pos_bottom , box2.pos_bottom)
		posL = min(box1.pos_left   , box2.pos_left)
		posR = max(box1.pos_right  , box2.pos_right)

		return Viewbox(posT,posB,posL,posR)

	if type(box1) == list and type(box2) == list:
		posT = max(box1[0], box2[0])
		posB = min(box1[1], box2[1])
		posL = min(box1[2], box2[2])
		posR = max(box1[3], box2[3])

		return Viewbox(posT,posB,posL,posR)

	if type(box1) == Viewbox and type(box2) == list:
		return updateViewbox([box1.pos_top,box1.pos_bottom,box1.pos_left,box1.pos_right], box2)

	if type(box1) == list and type(box2) == Viewbox:
		return updateViewbox(box1, [box2.pos_top,box2.pos_bottom,box2.pos_left,box2.pos_right])

def pathGenerate(polygon, VB, stroke="line"):
	path = ""

	if stroke == "line":

		for (i,position) in enumerate(polygon):
			if i == 0:
				ctrl = "M"
			else:
				ctrl = "L"

			path += f" {ctrl} {position[0]},{position[1]}"

			VB = updateViewbox(VB, [position[1],position[1],position[0],position[0]])

		return path, VB

	if stroke == "bezier":
		for (i,position) in enumerate(polygon):
			if i == 0:
				path += f" M {position[0]},{position[1]}"

			else:
				pass
			
		return path, VB

def polygon2Path(dtype, mpoly):
	VB = Viewbox()
	pathstr = ""

	if dtype == "Polygon":
		mpoly = [mpoly]
	
	for i in range(len(mpoly)):
		for poly in mpoly[i]:

			tpath, VB = pathGenerate(poly, VB)
			pathstr += tpath
	
	path = Path(pathstr, VB)

	return path

def geojson2html(geo, key=None):
	svghtml = "<svg viewbox=\"#viewbox\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" \">\n#polygon</svg>"
	polygonhtml = ""
	VB = Viewbox()

	for feature in geo.get("features",[]):
		
		# get properties
		props = feature.get("properties", {})
		prop_name = props.get("name", "")
		prop_fullname = props.get("fullname",prop_name)

		# skip not-specified
		if key != None and prop_name not in key:
			continue

		# get geometries
		geo = feature.get("geometry",{})
		geo_cors = geo.get("coordinates",[])
		geo_dtype = geo.get("type", None)

		if geo_dtype not in ["Polygon","MultiPolygon"]:
			print(f"Ops! {geo_dtype} can not be handled so far!")
			continue

		PATH = polygon2Path(geo_dtype, geo_cors)

		VB = updateViewbox(VB, PATH.box)

		polygonhtml += f"<path id=\"{prop_fullname}\" d=\"{PATH.path}\"><title>{prop_fullname}</title></path>\n"

	svghtml = svghtml.replace("#viewbox", " ".join(map(str, VB.shape())))
	svghtml = svghtml.replace("#polygon", polygonhtml)

	return svghtml

if __name__ == "__main__":
	import json

	html = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><title>Document</title></head><style>#style</style><body>#svg</body></html>"
	style = """
		svg {
			transform: scale(1,-1);
			height: 80vh;
			margin: 0 10vw;
			border: 1px solid black;
		}
		path,polygon {fill: white;
			stroke: black;
			stroke-width: 0.01;
		}
		path:hover,polygon:hover {
			fill: black;
			transition: 0.5s;
		}"""

	with open("./japan.json", "r", encoding="utf-8") as f:
		geo = json.load(f)

	html = html.replace("#svg", geojson2html(geo))
	html = html.replace("#style", style)
	
	with open("./geo.html", 'w', encoding="utf-8") as f:
		f.write(html)