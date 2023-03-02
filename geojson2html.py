# -*- encoding utf-8 -*-

import sys, os

#==============================================
#
# key : `name` property of `features` to draw
#       not set -> draw all the features
#
#==============================================

class Path:
	def __init__(self, position, viewbox):
		self.path = position
		self.box = viewbox

def updateViewbox(box, p:Path):
	posH = max(box[0], p.box[0])
	posB = min(box[1], p.box[1])
	posL = min(box[2], p.box[2])
	posR = max(box[3], p.box[3])
	box = [posH,posB,posL,posR]

	return box


def polygon2Path(dtype, mpoly):
	posH, posB, posL, posR = 0,1e10,1e10,0
	pathstr = ""

	if dtype == "Polygon":
		mpoly = [mpoly]
	
	for i in range(len(mpoly)):
		for poly in mpoly[i]:
			pathstr += f"M {poly[0][0]},{poly[0][1]}"

			for pos in poly[1:]:
				pathstr += f" L {pos[0]},{pos[1]}"
				posH = max(posH, pos[1])
				posB = min(posB, pos[1])
				posL = min(posL, pos[0])
				posR = max(posR, pos[0])

	viewbox = [posH,posB,posL,posR]
	
	path = Path(pathstr, viewbox)

	return path


def geojson2html(geo, key=None):
	svghtml = "<svg viewbox=\"#viewbox\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" style=\"transform: scale(1,-1);\">\n#polygon</svg>"
	polygonhtml = ""
	vb = [0,1e10,1e10,0]

	for feature in geo.get("features",[]):
		
		# get objects
		props = feature.get("properties", {})
		name = props.get("name", "")
		fullname = props.get("fullname",name)

		if key != None and name not in key:
			continue

		geo = feature.get("geometry",{})
		geocors = geo.get("coordinates",[])

		dtype = geo.get("type", None)

		if dtype != "Polygon" and dtype != "MultiPolygon":
			print(f"Ops! {dtype} can not be handled!")
			continue

		p = polygon2Path(dtype, geocors)

		vb = updateViewbox(vb, p)

		polygonhtml += f"<path id=\"{fullname}\" d=\"{p.path}\"><title>{fullname}</title></path>\n"

	svghtml = svghtml.replace("#viewbox", f"{vb[2]} {vb[1]} {vb[3]-vb[2]} {vb[0]-vb[1]}")
	svghtml = svghtml.replace("#polygon", polygonhtml)

	return svghtml

if __name__ == "__main__":
	import requests
	import json

	html = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><title>Document</title></head><style>svg {height: 80vh;margin: 0 10vw;border: 1px solid black;}path,polygon {fill: white;stroke: black;stroke-width: 0.01;}path:hover,polygon:hover {fill: black;transition: 0.5s;}</style><body>#svg</body></html>"

	def getGeoJsonChina():
		url = "https://geojson.cn/api/data/china.json"
		res = requests.get(url)

		if res.status_code == 200:
			geo = json.loads(res.content)

		return geo

	geo = getGeoJsonChina()
	html = html.replace("#svg", geojson2html(geo))
	fp = "./geo.html"
	
	with open(fp, 'w') as f:
		f.write(html)