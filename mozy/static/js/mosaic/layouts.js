var app = app || {};

$(function(){
    "use-strict";

    var MosaicLayout = Backbone.Marionette.LayoutView.extend({
        regions: {
            tiles: ".mosaic-tiles"
        }
    });

    app.MosaicLayout = MosaicLayout;
});

