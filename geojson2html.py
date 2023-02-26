# -*- encoding utf-8 -*-

import sys, os

#==============================================
#
# key : `name` property of `features` to draw
#       not set -> draw all the features
#
#==============================================

class Polygon:
	def __init__(self, position, viewbox):
		self.polygon = position
		self.box = viewbox


def geojson2html(geo, key=None):
	svghtml = "<svg viewbox=\"#viewbox\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" style=\"transform: scale(1,-1);\">\n#polygon</svg>"
	polygonhtml = ""
	vb = [0,1e10,1e10,0]

	for feature in geo.get("features",[]):

		# get name 
		props = feature.get("properties", {})
		name = props.get("name", "")
		fullname = props.get("fullname",name)

		if key == None or name in key:
			ps = geojson2strpoly(feature)

			for (i,p) in enumerate(ps):
				# add html polygon
				polygonhtml += f"<polygon id=\"{name}_{i+1}\" points=\"{p.polygon}\"><title>{fullname}</title></polygon>\n"

				# update svg viewbox
				posH = max(vb[0], p.box[0])
				posB = min(vb[1], p.box[1])
				posL = min(vb[2], p.box[2])
				posR = max(vb[3], p.box[3])
				vb = [posH,posB,posL,posR]

	svghtml = svghtml.replace("#viewbox", f"{vb[2]} {vb[1]} {vb[3]-vb[2]} {vb[0]-vb[1]}")
	svghtml = svghtml.replace("#polygon", polygonhtml)

	return svghtml
			

def geojson2strpoly(feature):
	# list of the polygon
	polygons = set([])

	# get coordinates
	geo = feature.get("geometry",{})
	dtype = geo.get("type", None)
	geocors = geo.get("coordinates",[])

	if dtype == "Polygon":
		polygons |= polygon2polygon(geocors)

	elif dtype == "MultiPolygon":
		for cor in geocors:
			polygons |= polygon2polygon(cor)

	else:
		print(
				f"Ops! {dtype} can not be handled!"
			)

	return polygons

def polygon2polygon(poly):
	polygons = set([])

	for cor in poly:
		polystr = ""
		posH, posB, posL, posR = 0,1e10,1e10,0

		for position in cor:
			polystr += f"{position[0]},{position[1]} "
			posH = max(posH, position[1])
			posB = min(posB, position[1])
			posL = min(posL, position[0])
			posR = max(posR, position[0])

		viewbox = [posH,posB,posL,posR]

		polygons.add(Polygon(polystr, viewbox))

	return polygons


if __name__ == "__main__":
	import requests
	import json

	def getGeoJsonChina():
		url = "https://geojson.cn/api/data/china.json"
		res = requests.get(url)

		if res.status_code == 200:
			geo = json.loads(res.content)

		return geo

	geo = getGeoJsonChina()
	svghtml = geojson2html(geo)
	fp = "./geo.html"
	
	with open(fp, 'w') as f:
		f.write(svghtml)