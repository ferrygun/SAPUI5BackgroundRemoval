sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/m/MessageToast"
], function(Controller, JSONModel, MessageToast) {
    jQuery.sap.require("Camera.lib.socketio");
    "use strict";
    var socket;
	var oModel;

	var IMAGE_PROCESSING_SRV = 'http://localhost:3000';
    socket = io(IMAGE_PROCESSING_SRV, { transport : ['websocket'] });

    socket.on('req', function(data) {
        sap.m.MessageToast.show("The image is ready now");
		console.log(data.base64);

		var aPhotosres = [];
		aPhotosres.push({
			src: data.base64
        });
		oModel.setProperty("/photosres", aPhotosres);
        oModel.refresh(true);
    });


    return Controller.extend("Camera.controller.Home", {
        onInit: function() {
            this.getView().setModel(new JSONModel({
                photos: []
            }));
        },

        /////////////////////////////////////////////
        //  EVENTS
        /////////////////////////////////////////////
        onSnapshot: function(oEvent) {
            // The image is inside oEvent, on the image parameter,
            // let's grab it.
            oModel = this.getView().getModel();
            var aPhotos = oModel.getProperty("/photos");

            socket.emit('client_data', {
                'base64': oEvent.getParameter("image")
            });

            aPhotos.push({
                src: oEvent.getParameter("image")
            });
            oModel.setProperty("/photos", aPhotos);
            oModel.refresh(true);
        },

        /**
         * Stop the camera when the tab is not visible.
         * @param {object} name
         * @returns {object}
         */
        onTabSelect: function(oEvent) {
            var oTab = oEvent.getParameter("key");
            var oCamera = this.getView().byId("idCamera");
            if (oTab !== "demo") {
                oCamera.stopCamera();
            } else {
                oCamera.rerender();
            }
        }
    });
});