window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, layer, context) {
                layer.bindTooltip(
                    '<div>' +
                    '<b>Address:</b> ' + feature.properties['Address'] + '<br>' +
                    '<b>id:</b> ' + feature.properties['id'] +
                    '</div>', {
                        permanent: false,
                        direction: 'top'
                    }
                );
            }

            ,
        function1: function(feature, latlng, context) {
                var preds = feature.properties.preds;
                var color = preds <= 0.5 ?
                    'rgb(' + Math.round(255 * (2 * preds)) + ', 255, 0)' :
                    'rgb(255, ' + Math.round(255 * (2 * (1 - preds))) + ', 0)';
                var radius = 5 + (10 * preds); // Base radius 5, max radius 15
                return L.circleMarker(latlng, {
                    radius: radius,
                    color: color,
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 1,
                    fillColor: color
                });
            }

            ,
        function2: function(feature, layer, context) {
            layer.bindTooltip(
                '<div>' +
                '<b>Address:</b> ' + feature.properties['Address'] + '<br>' +
                '<b>UNOM:</b> ' + feature.properties['UNOM'] + '<br>' +
                '<b>PREDICT:</b> ' + feature.properties['preds'] + '<br>' +
                '<b>Volume supplied (mean):</b> ' + feature.properties['volume_mean'] + '<br>' +
                '<b>Energy consumption (mean):</b> ' + feature.properties['energy_mean'] + '<br>' +
                '<b>Average temperature:</b> ' + feature.properties['temperature_mean'] + '<br>' +
                '<b>Number of complaints (mean):</b> ' + feature.properties['complaints_mean'] + '<br>' +
                '<b>Leakage (mean):</b> ' + feature.properties['leakage_mean'] + '<br>' +
                '<b>Error (mean):</b> ' + feature.properties['err_mean'] + '<br>' +
                '<b>Target max value:</b> ' + feature.properties['target_max'] + '<br>' +
                '<b>Walls:</b> ' + feature.properties['walls'] + '<br>' +
                '<b>Predicted series:</b> ' + feature.properties['predict_serie'] + '<br>' +
                '<b>Total area:</b> ' + feature.properties['total_area'] + '<br>' +
                '<b>Wear prediction:</b> ' + feature.properties['predict_wear'] + '<br>' +
                '<b>Age:</b> ' + feature.properties['old'] +
                '</div>', {
                    permanent: false,
                    direction: 'top'
                }
            );
        }

    }
});