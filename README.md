# geojson2html

geojson2html is a Python codes for rendering GeoJson to HTML (svg polygon)

## Usage

```python
import geojson2html

# plz prepare GeoJson 
geo = ...

# render properties named "Alaska" in GeoJson
svgHTML = geojson2html(geo, key="Alaska")

# render all the properties in GeoJson
# not set `key`
svgHTML = geojson2html(geo)
```

The output HTML is the following.

```html
<svg viewbox="{viewbox}" version="1.1" xmlns="http://www.w3.org/2000/svg">
<polygon id="{name}" points="{corrdinates}">
<title>{name/fullname}</title>
</polygon>
...
</svg>
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contacts/Information
[Twitter (@rj_phys)](https://www.twitter.com/rj_phys)

[Author WebSite](https://rjchiba.vercel.app)