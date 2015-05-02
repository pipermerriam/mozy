var app = app || {};

$(function(){
    "use-strict";

    var MosaicApplication = Backbone.Marionette.Application.extend({
        initialize: function(options) {
            this.mosaicImage = new app.MosaicImage({id: options.mosaicId});
            this.mosaicImage.fetch();

            this.mosaicTiles = new app.MosaicTiles([], {mosaicId: options.mosaicId});
            this.mosaicTiles.fetch();

            this.mosaicLayout = this.initializeLayout(options.el);
        },
        initializeLayout: function(el) {
            return new app.MosaicLayout({
                el: el
            });
        }
    });

    app.MosaicApplication = MosaicApplication;
});

