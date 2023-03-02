# geojson2html

geojson2html is a Python codes for rendering GeoJson to HTML (svg polygon)

## Usage

```python
from geojson2html import geojson2html

# plz prepare GeoJson 
geo = ...

# render properties named "Alaska" in GeoJson
html = geojson2html(geo, key="Alaska")

# render all the properties in GeoJson
# not set `key`
html = geojson2html(geo)
```

The output HTML is the following.

```html
...
<svg viewbox="{viewbox}" version="1.1" xmlns="http://www.w3.org/2000/svg">
<path id="{name}" points="{corrdinates}">
<title>{name/fullname}</title>
</path>
...
</svg>
...
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## See More

Qiita : [GeoJson を HTML に変換したい](https://qiita.com/RjChiba/items/5da96d3e4912d115344d)

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contacts/Information
[Twitter (@rj_phys)](https://www.twitter.com/rj_phys)

[Author's WebSite](https://rjchiba.vercel.app)