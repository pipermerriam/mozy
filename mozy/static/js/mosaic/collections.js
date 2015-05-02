var app = app || {};

$(function(){
    "use-strict";

    var MosaicTiles = Backbone.Collection.extend({
        model: app.MosaicImage
    });

    app.MosaicTiles = MosaicTiles;
});
