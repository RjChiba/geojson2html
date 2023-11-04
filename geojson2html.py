# -*- encoding utf-8 -*-

import sys, os
import traceback

#=== NOTICE ===========================================================
#
# The geographical data of Japan was kindly provided by japonyol.net
# https://japonyol.net/editor/article/47-prefectures-geojson.html
# 
#======================================================================

def perpendicular_distance(point, line_start, line_end):
    # Calculate the perpendicular distance from `point` to the line defined by `line_start` and `line_end`.
    x, y = point
    x1, y1 = line_start
    x2, y2 = line_end

    numerator = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1)
    denominator = ((y2 - y1) ** 2 + (x2 - x1) ** 2)**0.5

    return numerator / denominator

def douglas_peucker_simplify(polygon, tolerance):
    if len(polygon) <= 2:
        # The polygon is too small to simplify further.
        return polygon

    # Find the point with the maximum perpendicular distance
    max_distance = 0
    max_index = 0
    start, end = polygon[0], polygon[-1]

    for i in range(1, len(polygon) - 1):
        distance = perpendicular_distance(polygon[i], start, end)
        if distance > max_distance:
            max_distance = distance
            max_index = i

    if max_distance > tolerance:
        # If the maximum distance is greater than the tolerance, split the polygon and simplify each half
        first_half = douglas_peucker_simplify(polygon[:max_index + 1], tolerance)
        second_half = douglas_peucker_simplify(polygon[max_index:], tolerance)
        # Combine the two halves into a simplified polygon
        return first_half[:-1] + second_half
    else:
        # If the maximum distance is not greater than the tolerance, simply return the start and end points
        return [start, end]

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

def pathGenerate(polygon, VB, stroke):
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

	if stroke == "beizer":
		for (i,position) in enumerate(polygon):
			ip = (i+1)%len(polygon)
			ib = (i-1)%len(polygon)

			beizer_ref = [
				polygon[ip][0] - polygon[ib][0], polygon[ip][1] - polygon[ib][1]
			]
			L2norm = (beizer_ref[0]**2 + beizer_ref[1]**2)**0.5
			beizer_ref = [x * L2norm for x in beizer_ref]
			beizer_point = [ - x + y for (x,y) in zip(beizer_ref, position)]

			if i == 0:
				path += f" M {position[0]},{position[1]} C {beizer_point[0]},{beizer_point[1]}"

			elif i == 1:
				path += f", {beizer_point[0]},{beizer_point[1]} {position[0]},{position[1]}"
			
			else:
				path += f" S {beizer_point[0]},{beizer_point[1]} {position[0]},{position[1]}"

			VB = updateViewbox(VB, [position[1],position[1],position[0],position[0]])
			
		return path, VB

def polygon2Path(dtype, mpoly, stroke):
	VB = Viewbox()
	pathstr = ""

	if dtype == "Polygon":
		mpoly = [mpoly]
	
	for i in range(len(mpoly)):
		for poly in mpoly[i]:

			tpath, VB = pathGenerate(poly, VB, stroke)
			pathstr += tpath
	
	path = Path(pathstr, VB)

	return path

def geojson2html(geo, key=None, stroke="line"):
	svghtml = "<svg viewbox=\"#viewbox\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\">\n#polygon</svg>"
	polygonhtml = ""
	VB = Viewbox()

	if type(key) == str or key == None:
		key = [key]

	for feature in geo.get("features",[]):
		
		# get properties
		props = feature.get("properties", {})
		prop_name = props.get("name", "")
		prop_fullname = props.get("fullname",prop_name)

		for k in key:
			# skip not-specified
			if k != None and prop_name not in k:
				continue

			# get geometries
			geo = feature.get("geometry",{})
			geo_cors = geo.get("coordinates",[])
			geo_dtype = geo.get("type", None)

			if geo_dtype not in ["Polygon","MultiPolygon"]:
				print(f"Ops! {geo_dtype} can not be handled so far!")
				continue

			PATH = polygon2Path(geo_dtype, geo_cors, stroke)

			VB = updateViewbox(VB, PATH.box)

			polygonhtml += f"<path id=\"{prop_fullname}\" d=\"{PATH.path}\"><title>{prop_fullname}</title></path>\n"

	svghtml = svghtml.replace("#viewbox", " ".join(map(str, VB.shape())))
	svghtml = svghtml.replace("#polygon", polygonhtml)

	return svghtml, VB

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
			stroke-width: #stroke_width;
		}
		path:hover,polygon:hover {
			fill: darkgray;
			transition: 0.5s;
		}"""

	with open("./japan.json", "r", encoding="utf-8-sig") as f:
		geo = json.load(f)

	geohtml, VB = geojson2html(geo, stroke="beizer")

	html = html.replace("#svg", geohtml)
	html = html.replace("#style", style)
	html = html.replace("#stroke_width", str((VB.pos_top - VB.pos_bottom)/1000))
	
	with open("./geo2.html", 'w', encoding="utf-8") as f:
		f.write(html)