# geojson2html

geojson2html is a Python codes for rendering GeoJson to HTML (svg polygon)

## Usage

```python
from geojson2html import geojson2html

# prepare GeoJson 
geo = ...

# render properties named "Alaska" in GeoJson
html = geojson2html(geo, key="Alaska")

# render all the properties in GeoJson
# not set `key`
html = geojson2html(geo)
```
```python
# default curve-type is "linear"
html = geojson2html(geo, stroke="linear")
# same as
html = geojson2html(geo)

# set curve-type to "bezier"
html = geojson2html(geo, stroke="bezier")
```

The output HTML has the followin format:

```html
...
<svg viewbox="{viewbox}" version="1.1" xmlns="http://www.w3.org/2000/svg">
<path id="{name}" points="{corrdinates}"><title>{name/fullname}</title></path>
...
</svg>
...
```

## Use case
[開拓団入植地 - 満洲開拓資料館](https://mus-manchuria.com/ja/document/)

## Contributing
Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## ChangeLog

### 1.1.0
- Add `stroke` option
- Add `bezier` curve-type
- Fix bugs
- Changed the innner structure of the codes

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contacts/Information
[Twitter (@rj_phys)](https://www.twitter.com/rj_phys)

[Author's WebSite](https://rjchiba.vercel.app)
