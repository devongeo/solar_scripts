/********************** The Map itself ***************************/
// Make the map object itself. At this point it doesn't have any
// layers or even a basemap
var map = L.map('map');
map.setView([46,-93],7);

/*********************** Base map ******************************/

// Let's set some basemap options
var tile_options = {
    subdomains: '1234', // Using multiple subdomains allows the user to download more tiles at a time so
    attribution: 'Map data OpenStreeMaps and MapQuest'
};

// Now we add the actual tile layer
var basemap = L.tileLayer('http://otile{s}.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.png',tile_options);
basemap.addTo(map);

var colormap = {
    '-3' : '#ff0000',
    '-2' : '#cdcdcd',
    '-1' : '#cdcdcd',
    '0'  : '#f5bc5f',
    '1'  : '#5fe7f5',
    '2'  : '#5ff564'
};


function style(feature) {
    return {
        fillColor: colormap[feature.properties.state],
        weight: 2,
        opacity: 0.4,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.4
    };
}

function sastyle(feature){
    return {
        fillColor: '#ffffff',
        fillOpacity: 0.0,

        color: '#e2e200',
        opacity: 0.9,
        weight: 0.8
    };
}

function bboxStyle(feature){
    return {
        fillColor: '#ffffff',
        fillOpacity: 0.0,

        color: '#5f3764',
        opacity: 0.8,
        weight: 0.8
    };
}

function makePopup(feature,layer){
    html = "<dl>";
    for(var f in feature.properties){
        html += "<dt>" + f + "</dt><dd>" + feature.properties[f] + "</dd>";
    }
    html += "</dl>";
    layer.bindPopup(html);
}

layers = {
    dem_fishnet: L.geoJson(null,{onEachFeature:makePopup,style:style}).addTo(map),
    lidar_bbox: L.geoJson(null,{onEachFeature:makePopup,style:bboxStyle}),
    sa_fishnet: L.geoJson(null,{onEachFeature:makePopup,style:sastyle})
};

L.control.layers(null,layers).addTo(map);

$.getJSON("./js/dem_fishnets.py",function(json){ layers.dem_fishnet.addData(json); });
$.getJSON("./js/lidar_bbox.py",function(json){ layers.lidar_bbox.addData(json); });
//$.getJSON("./js/sa_fishnets.py",function(json){ layers.dem_fishnet.addData(json); });
