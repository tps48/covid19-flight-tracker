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

      //Add state layer

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

      //Add county layer

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
      
      //Add airport markers

      // Add an image to use as a custom marker
      map.loadImage('https://docs.mapbox.com/mapbox-gl-js/assets/custom_marker.png',
      function (error, image) {
          if (error) throw error;
          map.addImage('custom-marker', image);

          map.addSource('airports', {
            'type': 'geojson',
            'data': '/airportData'
          });

          map.addLayer({
            'id': 'airports',
            'type': 'symbol',
            'source': 'airports',
            'layout': {
              'icon-image': 'custom-marker',
              'icon-allow-overlap': true
            }
          });
        }
      );

      //Create popup to be added later
      var popup = new mapboxgl.Popup({
        closeButton: false,
        closeOnClick: false
      });

      map.on('mouseenter','airports', function (e) {

        //Change cursor for user benefit 
        map.getCanvas().style.cursor = 'pointer';

        var coordinates = e.features[0].geometry.coordinates.slice();
        var name = e.features[0].properties.name.toUpperCase();

        //This math function ensures the pop-up is the one being hovered
        //over. Helps prevent bugs when zooming in and out 
        while(Math.abs(e.lngLat.lng - coordinates[0]) >180) {
          coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }

        popup.setLngLat(coordinates).setHTML(name).addTo(map);
      });

      //Closes popup when hover stops
      map.on('mouseleave', 'airports', function () {
        map.getCanvas().style.cursor = '';
        popup.remove();
      });
    
    }); //map.on('load')

    //Switch between state layer and county layer
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

    //Filter airports based on input
    var covidMinFilter = document.getElementById('mincases');
    var covidMaxFilter = document.getElementById('maxcases');
    var filterButton = document.getElementById('filter');

    filterButton.addEventListener('click', event => {
      console.log('filtering...');
      minCases = covidMinFilter.value;
      maxCases = covidMaxFilter.value;
      if(minCases.length == 0 && maxCases.length == 0) {
        console.log('No filter input');
      }
      else {
        map.removeLayer('airports');
        map.removeSource('airports');
        if(minCases.length != 0 && maxCases.length != 0) {
          var path = '/airportData/minMax/'+minCases+'/'+maxCases;
          map.addSource('airports', {
                'type': 'geojson',
                'data': path
          }); 
        }
        else if(minCases.length == 0) {
          var path = '/airportData/max/'+maxCases;
          map.addSource('airports', {
                'type': 'geojson',
                'data': path
          }); 
        }
        else if(maxCases.length == 0) {
          var path = '/airportData/min/'+minCases;
          map.addSource('airports', {
                'type': 'geojson',
                'data': path
          }); 
        }
        map.addLayer({
          'id': 'airports',
          'type': 'symbol',
          'source': 'airports',
          'layout': {
            'icon-image': 'custom-marker',
            'icon-allow-overlap': true
          }
        }); 
      }
    });

    //Reset the airport filter when reset button is clicked
    resetButton = document.getElementById('reset');
    resetButton.addEventListener('click', event => {
      console.log('Resetting airports');
      map.removeLayer('airports');
      map.removeSource('airports');
      map.addSource('airports', {
        'type': 'geojson',
        'data': '/airportData'
      });

      map.addLayer({
        'id': 'airports',
        'type': 'symbol',
        'source': 'airports',
        'layout': {
          'icon-image': 'custom-marker',
          'icon-allow-overlap': true
        }
      });
    });

    searchAirport = document.getElementById('airportcode');
    searchButton = document.getElementById('search');
    searchButton.addEventListener('click', event => {
      var source = map.getSource('foundAirport');
      if(typeof source != 'undefined') {
        map.removeSource('foundAirport');
      }
      path = /findAirport/+searchAirport.value;
      map.addSource('foundAirport', {
        'type': 'geojson',
        'data': path
      });
      console.log('Loaded.');
    });


    map.getCanvas().style.cursor = 'default';

    map.fitBounds([[-133.2421875, 16.972741], [-47.63671875, 52.696361]]);