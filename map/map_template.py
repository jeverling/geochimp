"""Template for creating a map with markers for camera trap locations.

Currently, we only display the first image for each camera trap.
This needs to be changed to include all images - or, if that's not supported, we could
create a thumbnail with preview of all photos and link to a page where they are
displayed, or present them in some other way. But maybe there is a way to add multiple
photos to a pop-up.
"""


# f-strings are nice, but not with too many curly brackets
# @TODO: make sure %f formatter doesn't truncate value
single_feature_template = """
{
  "geometry": {
    "x": %(x)f,
    "y": %(y)f,
    "spatialReference": { "wkid": 102100, "latestWkid": 3857 }
  },
  "attributes": {
    "VISIBLE": 1,
    "TYPEID": 0,
    "TITLE": "%(title)s",
    "IMAGE_URL": "%(image_url)s",
    "DESCRIPTION": "<span style='background-color: rgb(255, 255, 255);'>%(description)s<br /></span>"
  }
}
"""  # noqa: E501

# @TODO: reduce this to the minimum necessary
map_template = """
{
  "operationalLayers": [
    {
      "layerType": "ArcGISFeatureLayer",
      "featureCollectionType": "notes",
      "id": "mapNotes_7824",
      "title": "Camera trap locations",
      "featureCollection": {
        "layers": [
          {
            "popupInfo": {
              "mediaInfos": [
                {
                  "type": "image",
                  "value": {
                    "sourceURL": "{IMAGE_URL}",
                    "linkURL": "{IMAGE_LINK_URL}"
                  }
                }
              ],
              "description": "{DESCRIPTION}",
              "title": "{TITLE}"
            },
            "layerDefinition": {
              "templates": [],
              "drawingInfo": {
                "renderer": {
                  "uniqueValueInfos": [
                    {
                      "symbol": {
                        "contentType": "image/png",
                        "url": "https://static.arcgis.com/images/Symbols/Basic/GreenStickpin.png",
                        "yoffset": 12,
                        "width": 24,
                        "height": 24,
                        "type": "esriPMS",
                        "xoffset": 0
                      },
                      "description": "",
                      "value": "0",
                      "label": "Stickpin"
                    },
                    {
                      "symbol": {
                        "contentType": "image/png",
                        "url": "https://static.arcgis.com/images/Symbols/Basic/GreenShinyPin.png",
                        "yoffset": 8,
                        "width": 24,
                        "height": 24,
                        "type": "esriPMS",
                        "xoffset": 2
                      },
                      "value": "1",
                      "label": "Pushpin"
                    },
                    {
                      "symbol": {
                        "color": [155, 187, 89, 128],
                        "style": "esriSMSCross",
                        "type": "esriSMS",
                        "outline": {
                          "color": [115, 140, 61, 255],
                          "width": 1,
                          "style": "esriSLSSolid",
                          "type": "esriSLS"
                        },
                        "size": 18
                      },
                      "value": "2",
                      "label": "Cross"
                    }
                  ],
                  "field1": "TYPEID",
                  "type": "uniqueValue"
                }
              },
              "displayField": "TITLE",
              "name": "Points",
              "hasAttachments": false,
              "fields": [
                {
                  "editable": false,
                  "alias": "OBJECTID",
                  "type": "esriFieldTypeOID",
                  "name": "OBJECTID"
                },
                {
                  "editable": true,
                  "alias": "Title",
                  "length": 255,
                  "type": "esriFieldTypeString",
                  "name": "TITLE"
                },
                {
                  "editable": true,
                  "alias": "Visible",
                  "type": "esriFieldTypeInteger",
                  "name": "VISIBLE"
                },
                {
                  "editable": true,
                  "alias": "Description",
                  "length": 1073741822,
                  "type": "esriFieldTypeString",
                  "name": "DESCRIPTION"
                },
                {
                  "editable": true,
                  "alias": "Image URL",
                  "length": 255,
                  "type": "esriFieldTypeString",
                  "name": "IMAGE_URL"
                },
                {
                  "editable": true,
                  "alias": "Image Link URL",
                  "length": 255,
                  "type": "esriFieldTypeString",
                  "name": "IMAGE_LINK_URL"
                },
                {
                  "editable": true,
                  "alias": "DATE",
                  "length": 36,
                  "type": "esriFieldTypeDate",
                  "name": "DATE"
                },
                {
                  "editable": true,
                  "alias": "Type ID",
                  "type": "esriFieldTypeInteger",
                  "name": "TYPEID"
                }
              ],
              "capabilities": "Query,Editing",
              "visibilityField": "VISIBLE",
              "geometryType": "esriGeometryPoint",
              "typeIdField": "TYPEID",
              "objectIdField": "OBJECTID",
              "type": "Feature Layer",
              "types": [
                {
                  "templates": [
                    {
                      "prototype": {
                        "attributes": {
                          "VISIBLE": 1,
                          "TYPEID": 0,
                          "TITLE": "Point"
                        }
                      },
                      "drawingTool": "esriFeatureEditToolPoint",
                      "description": "",
                      "name": "Stickpin"
                    }
                  ],
                  "domains": {},
                  "id": 0,
                  "name": "Stickpin"
                },
                {
                  "templates": [
                    {
                      "prototype": {
                        "attributes": {
                          "VISIBLE": 1,
                          "TYPEID": 1,
                          "TITLE": "Point"
                        }
                      },
                      "drawingTool": "esriFeatureEditToolPoint",
                      "description": "",
                      "name": "Pushpin"
                    }
                  ],
                  "domains": {},
                  "id": 1,
                  "name": "Pushpin"
                },
                {
                  "templates": [
                    {
                      "prototype": {
                        "attributes": {
                          "VISIBLE": 1,
                          "TYPEID": 2,
                          "TITLE": "Point"
                        }
                      },
                      "drawingTool": "esriFeatureEditToolPoint",
                      "description": "",
                      "name": "Cross"
                    }
                  ],
                  "domains": {},
                  "id": 2,
                  "name": "Cross"
                }
              ],
              "extent": {
                "xmin": 802430.2550109352,
                "ymin": 6555974.341802447,
                "xmax": 802430.2552109351,
                "ymax": 6555974.342002447,
                "spatialReference": { "wkid": 102100, "latestWkid": 3857 }
              },
              "spatialReference": { "wkid": 102100, "latestWkid": 3857 }
            },
            "featureSet": {
              "geometryType": "esriGeometryPoint",
              "features": []
            }
          }
        ],
        "showLegend": false
      },
      "opacity": 1,
      "visibility": true
    }
  ],
  "baseMap": {
    "baseMapLayers": [
      {
        "id": "World_Imagery_2017",
        "layerType": "ArcGISTiledMapServiceLayer",
        "url": "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer",
        "visibility": true,
        "opacity": 1,
        "title": "World Imagery"
      },
      {
        "id": "VectorTile_7259",
        "type": "VectorTileLayer",
        "layerType": "VectorTileLayer",
        "title": "Hybrid Reference Layer",
        "styleUrl": "https://cdn.arcgis.com/sharing/rest/content/items/30d6b8271e1849cd9c3042060001f425/resources/styles/root.json",
        "isReference": true,
        "visibility": true,
        "opacity": 1
      }
    ],
    "title": "Imagery Hybrid"
  },
  "spatialReference": { "wkid": 102100, "latestWkid": 3857 },
  "authoringApp": "WebMapViewer",
  "authoringAppVersion": "10.2",
  "version": "2.25"
}
"""  # noqa: E501
