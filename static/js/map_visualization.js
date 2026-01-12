/**
 *
 *  VISUALIZE MAP
 *
 **/

function visualize_map(method, countries_data, params = {}){
    var geojson;
    var cluster_type = false;
    var percent = false;
    if (!(jQuery.isEmptyObject(params))){
        if ('cluster_type' in params){
            cluster_type = true;
        }
        if ('percent' in params){
            percent = params['percent'];
        }
    }

    /**
    MAP FUNCTIONS
     Based on:
    Leaflet (n. d.) Interactive Choropleth Map. Retrieved October 25, 2019 from https://leafletjs.com/examples/choropleth/
    **/

    function highlightFeature(e) {
        var this_layer = e.target;
        var feature_array = [this_layer];
        if (method === 'cluster') {
            geojson.eachLayer(function(layer) {
                if (layer.feature.properties.cluster === this_layer.feature.properties.cluster){
                    feature_array.push(layer);
                }
            });
        }

        for (i = 0; i < feature_array.length; i++) {
            feature_array[i].setStyle({
                weight: 5,
                color: '#666',
                dashArray: '',
                fillOpacity: 0.7
            });

            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                feature_array[i].bringToFront();
            }
        }
        info.update(this_layer.feature.properties);
    }

    function resetHighlight(e) {
        var this_layer = e.target;
        var feature_array = [this_layer];
        if (method === 'cluster') {
            geojson.eachLayer(function(layer) {
                if (layer.feature.properties.cluster === this_layer.feature.properties.cluster){
                    feature_array.push(layer);
                }
            });
        }

        for (i = 0; i < feature_array.length; i++) {
            geojson.resetStyle(feature_array[i]);
        }
        info.update();
    }


    /**
     * when you click on a country area this function gets triggered and activates the graph visualization for the cluster
     */
    function trigger_count_country(e){
        var layer = e.target;
        if (method === 'cluster') {
            var country_ids = [];
            for (var key in countries_data) {
                if (countries_data[key]['count'] === countries_data[layer.feature.properties.CNTR_CODE.toLowerCase()]['count']) {
                    country_ids.push(key);
                }
            }
            var cluster = countries_data[layer.feature.properties.CNTR_CODE.toLowerCase()]['count'];
            if (cluster_type === true && params['cluster_type'] === 'publication_timeline') {

                activateMethod('publication_timeline', {'countries': country_ids, 'cluster': cluster});
            } else if (cluster_type === true && params['cluster_type'] === 'formats') {

                activateMethod('formats', {'countries': country_ids, 'cluster': cluster});
            } else if (cluster_type === true && params['cluster_type'] === 'categories') {

                activateMethod('categories', {'countries': country_ids, 'cluster': cluster});
            }
            else {
                 activateMethod('count_country', {'country_id': layer.feature.properties.CNTR_CODE.toLowerCase()});
            }
        }
        else if (percent === 'licenses' || percent === 'empty_licenses'){
            activateMethod('country_licenses', {'country_id': layer.feature.properties.CNTR_CODE.toLowerCase()});
        }
        else {
            activateMethod('count_country', {'country_id': layer.feature.properties.CNTR_CODE.toLowerCase()});
        }
    }


    /**
    create an on-event for each country tile that lets you interact with the country on the map
     **/
    function onEachFeature(feature, layer) {
        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
            click: trigger_count_country
        });
    }

    function getColor(d) {
        /**
         color palette from:
         http://colorbrewer2.org/#type=sequential&scheme=Greys&n=9
         **/
        return d > 100000 ? '#800026' :
               d > 50000 ? '#bd0026' :
               d > 25000  ? '#e31a1c' :
               d > 10000  ? '#fc4e2a' :
               d > 5000  ? '#fd8d3c' :
               d > 1000   ? '#feb24c' :
               d > 500   ? '#fed976' :
               d > 100   ? '#ffeda0' :
                          '#ffffcc';
    }

    function getColorPercent(d) {
        /**
         color palette from:
         http://colorbrewer2.org/#type=sequential&scheme=Greys&n=9
         **/
        if (d === 0) return '#bdbdbd';
        else return d > 90 ? '#4b0017' :
               d > 80 ? '#800026' :
               d > 70 ? '#bd0026' :
               d > 60  ? '#e31a1c' :
               d > 50  ? '#fc4e2a' :
               d > 40  ? '#fd8d3c' :
               d > 30   ? '#feb24c' :
               d > 20   ? '#fed976' :
               d > 10   ? '#ffeda0' :
                          '#ffffcc';
    }

    function getColorClusters(d) {
        /**
         colors from:
         http://colorbrewer2.org/#type=qualitative&scheme=Paired&n=12
         **/
        var colors = ['#e31a1c', '#1f78b4', '#33a02c', '#6a3d9a', '#ff7f00', '#dce31a',  '#b2df8a', '#fb9a99', '#cab2d6', '#fdbf6f', '#ffff99'];
        return colors[d];
    }

    //feature.properties.CNTR_CODE
    function style(feature) {
        var color;
        //console.log(feature.properties.CNTR_CODE);

        if (feature.properties.CNTR_CODE.toLowerCase() in countries_data) {
            var count_forColor = parseFloat(countries_data[feature.properties.CNTR_CODE.toLowerCase()]['count']);
            if (method === 'count') {
                if (percent) color = getColorPercent(count_forColor);
                else color = getColor(count_forColor);
            }
            else if (method === 'cluster'){
                // -1 because clusters start with 1 but we want color array[0]
                color = getColorClusters(count_forColor - 1);
            }
        } else color = '#bdbdbd';

        return {
            fillColor: color,
            weight: 1,
            opacity: 1,
            color: '#969696',
            //dashArray: '3',
            fillOpacity: 1
        };
    }

    /**
     * INIT MAP
     */

    document.getElementById('visualization').innerHTML = "<div id='europe_map'></div>";

    var map = L.map('europe_map').setView([50.5393851,9.7867332], 4);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    /**
    european borders
    https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/nuts
    **/
    $.ajax({
        type: 'POST',
        url: "/_get_european_borders",
        dataType: "json",
        success: function(data){
            if (data['status'] == 'OK') {
                european_borders = data['data']['european_borders_geojson'];
                //var test_codes = {};
                if (method == 'cluster'){
                    for (i = 0; i < european_borders['features'].length; i++) {
                        //test_codes[european_borders['features'][i]['properties']['NUTS_NAME']] = european_borders['features'][i]['properties'].CNTR_CODE.toLowerCase();
                        if(european_borders['features'][i]['properties'].CNTR_CODE.toLowerCase() in countries_data) {
                            european_borders['features'][i]['properties']['cluster'] = countries_data[european_borders['features'][i]['properties'].CNTR_CODE.toLowerCase()]['count'];
                        }
                    }
                }
                //console.log('test_codes');
                //console.log(test_codes);
                geojson = L.geoJson(european_borders, {
                    onEachFeature: onEachFeature,
                    style: style
                }).addTo(map);
            }
            else console.log('Could not load european borders geojson.');
        }
    });


    /**
    * INFO
    */

    var info = L.control();

    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
        this.update();
        return this._div;
    };

    // method that we will use to update the control based on feature properties passed
    info.update = function (props) {
        if (method === 'count') {
            if (typeof percent === 'string') {
                if (percent === 'licenses') {
                    this._div.innerHTML = '<h4>Open Licenses</h4>' + (props && props.CNTR_CODE.toLowerCase() in countries_data ?
                        '<b>' + countries_data[props.CNTR_CODE.toLowerCase()]['country_title'] + '</b><br />' + countries_data[props.CNTR_CODE.toLowerCase()]['count'] + ''
                        : 'Click on a country for more information');
                }
                else if (percent === 'empty_licenses') {
                    this._div.innerHTML = '<h4>Datasets with License</h4>' + (props && props.CNTR_CODE.toLowerCase() in countries_data ?
                        '<b>' + countries_data[props.CNTR_CODE.toLowerCase()]['country_title'] + '</b><br />' + countries_data[props.CNTR_CODE.toLowerCase()]['count'] + ''
                        : 'Click on a country for more information');
                }
                else if (percent === 'accessible') {
                    this._div.innerHTML = '<h4>Accessible Datasets</h4>' + (props && props.CNTR_CODE.toLowerCase() in countries_data ?
                        '<b>' + countries_data[props.CNTR_CODE.toLowerCase()]['country_title'] + '</b><br />' + countries_data[props.CNTR_CODE.toLowerCase()]['count'] + ''
                        : 'Click on a country for more information');
                }
                else if (percent === 'linked') {
                    this._div.innerHTML = '<h4>Linked Data Support</h4>' + (props && props.CNTR_CODE.toLowerCase() in countries_data ?
                        '<b>' + countries_data[props.CNTR_CODE.toLowerCase()]['country_title'] + '</b><br />' + countries_data[props.CNTR_CODE.toLowerCase()]['count'] + ''
                        : '');
                }
            }
            else {
                this._div.innerHTML = '<h4>Number of datasets</h4>' + (props && props.CNTR_CODE.toLowerCase() in countries_data ?
                '<b>' + countries_data[props.CNTR_CODE.toLowerCase()]['country_title'] + '</b><br />' + countries_data[props.CNTR_CODE.toLowerCase()]['count'] + ''
                : 'Click on a country for more information');
            }
        }
        else if (method === 'cluster'){
            var title = '';

            if (cluster_type === true && params['cluster_type'] === 'publication_timeline') {
                title = 'Timeliness of release';
            } else if (cluster_type === true && params['cluster_type'] === 'formats') {
                title = 'Open Formats';
            } else if (cluster_type === true && params['cluster_type'] === 'categories') {
                title = 'Thematic categories';
            }
            else title = 'Clustering';

            if ('n_clusters' in params){
                title += '<br>'+ params['n_clusters'] +' Clusters';
            }

            this._div.innerHTML = '<h4>'+ title +'</h4>' + (props && props.CNTR_CODE.toLowerCase() in countries_data ?
                '<b>' + countries_data[props.CNTR_CODE.toLowerCase()]['country_title'] + '</b><br />Cluster ' + countries_data[props.CNTR_CODE.toLowerCase()]['count'] + ''
                : 'Click on a country for more information');
        }
    };

    info.addTo(map);

    /**
     * LEGEND
     */
    if (method == 'count') {

        var legend = L.control({position: 'bottomright'});

        legend.onAdd = function (map) {
            if (typeof percent === 'string'){
                var grades = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90];
            }
            else var grades = [1, 100, 500, 1000, 5000, 10000, 25000, 50000, 100000];

            var div = L.DomUtil.create('div', 'info legend'),
                grades,
                labels = [];

            div.innerHTML += '<i style="background:#bdbdbd"></i> 0<br>';

            for (var i = 0; i < grades.length; i++) {
                if (typeof percent === 'string'){
                    div.innerHTML +=
                        '<i style="background:' + getColorPercent(grades[i] + 1) + '"></i> ' +
                        grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
                }
                else {
                    div.innerHTML +=
                        '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
                        grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
                }
            }

            return div;
        };

        legend.addTo(map);
    }

    return map;
}