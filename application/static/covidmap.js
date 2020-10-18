mapboxgl.accessToken = 'pk.eyJ1Ijoic2VuaW9ycHJvamVjdGRqdCIsImEiOiJja2ZiZDgzaDUwcWN0MnFxZWFtaXpyeGw0In0.EVOg-lEJG4XJqlB0l706qQ'; // replace this with your access token
    var map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/seniorprojectdjt/ckfbiqp964g9o19lnubz33fnq', // replace this with your style URL
    });
    // code from the next step will go here

    map.on('load', function() {
      var layers = map.getStyle().layers;
      // Find the index of the first symbol layer in the map style
      var firstSymbolId;
      for (var i = 0; i < layers.length; i++) {
        if (layers[i].type === 'symbol') {
          firstSymbolId = layers[i].id;
          break;
        }
      }

      map.addSource('state-numbers', {
        'type': 'geojson',
        'data': '/stateData'
      });

      console.log('loading state data...')

      map.addLayer({
        'id': 'state-fill',
        'type': 'fill',
        'source': 'state-numbers',
        'layout': {},
        'paint': {
          'fill-color': [
            'rgb',
            240,
            ['max', ['-', 240, ['/', ['get', 'cases'], 100]], 0],
            ['max', ['-', 240, ['/', ['get', 'cases'], 100]], 0]
          ],
          'fill-opacity': 0.4
        }
      }, firstSymbolId);

      map.addSource('county-numbers', {
        'type': 'geojson',
        'data': '/countyData'
      });

      console.log('loading county data...')

      map.addLayer({
        'id': 'county-fill',
        'type': 'fill',
        'source': 'county-numbers',
        'layout': {
          'visibility': 'none'
        },
        'paint': {
          'fill-color': [
            'rgb',
            240,
            ['max', ['-', 240, ['/', ['get', 'cases'], 5]], 0],
            ['max', ['-', 240, ['/', ['get', 'cases'], 5]], 0]
          ],
          'fill-opacity': 0.4
        }
      }, firstSymbolId);
      
    });

    var list = document.getElementById('layer');
    list.addEventListener('change', (event) => {
      console.log('toggling');
      var selected = list.selectedIndex;
      console.log(event.target.value);
      
      if(event.target.value == 'state') {
        map.setLayoutProperty('state-fill', 'visibility', 'visible');
        map.setLayoutProperty('county-fill', 'visibility', 'none');
      }
      else if(event.target.value == 'county') {
        map.setLayoutProperty('state-fill', 'visibility', 'none');
        map.setLayoutProperty('county-fill', 'visibility', 'visible');
      }
    });



    map.getCanvas().style.cursor = 'default';

    map.fitBounds([[-133.2421875, 16.972741], [-47.63671875, 52.696361]]);