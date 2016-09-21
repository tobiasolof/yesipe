require=(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({"Pointer":[function(require,module,exports){
exports.Pointer = (function() {
  var clientCoords, coords, offsetArgumentError, offsetCoords, screenArgumentError;

  function Pointer() {}

  Pointer.screen = function(event, layer) {
    var e, screenCoords;
    if (!((event != null) && (layer != null))) {
      screenArgumentError();
    }
    e = offsetCoords(event);
    if (e.x && e.y) {
      screenCoords = layer.screenFrame;
      e.x += screenCoords.x;
      e.y += screenCoords.y;
    } else {
      e = clientCoords(event);
    }
    return e;
  };

  Pointer.offset = function(event, layer) {
    var e, targetScreenCoords;
    if (!((event != null) && (layer != null))) {
      offsetArgumentError();
    }
    e = offsetCoords(event);
    if (!((e.x != null) && (e.y != null))) {
      e = clientCoords(event);
      targetScreenCoords = layer.screenFrame;
      e.x -= targetScreenCoords.x;
      e.y -= targetScreenCoords.y;
    }
    return e;
  };

  offsetCoords = function(ev) {
    var e;
    e = Events.touchEvent(ev);
    return coords(e.offsetX, e.offsetY);
  };

  clientCoords = function(ev) {
    var e;
    e = Events.touchEvent(ev);
    return coords(e.clientX, e.clientY);
  };

  coords = function(x, y) {
    return {
      x: x,
      y: y
    };
  };

  screenArgumentError = function() {
    error(null);
    return console.error("Pointer.screen() Error: You must pass event & layer arguments. \n\nExample: layer.on Events.TouchStart,(event,layer) -> Pointer.screen(event, layer)");
  };

  offsetArgumentError = function() {
    error(null);
    return console.error("Pointer.offset() Error: You must pass event & layer arguments. \n\nExample: layer.on Events.TouchStart,(event,layer) -> Pointer.offset(event, layer)");
  };

  return Pointer;

})();


},{}],"TextLayer":[function(require,module,exports){
var TextLayer, convertTextLayers, convertToTextLayer,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

TextLayer = (function(superClass) {
  extend(TextLayer, superClass);

  function TextLayer(options) {
    if (options == null) {
      options = {};
    }
    this.doAutoSize = false;
    this.doAutoSizeHeight = false;
    if (options.backgroundColor == null) {
      options.backgroundColor = options.setup ? "hsla(60, 90%, 47%, .4)" : "transparent";
    }
    if (options.color == null) {
      options.color = "red";
    }
    if (options.lineHeight == null) {
      options.lineHeight = 1.25;
    }
    if (options.fontFamily == null) {
      options.fontFamily = "Helvetica";
    }
    if (options.fontSize == null) {
      options.fontSize = 20;
    }
    if (options.text == null) {
      options.text = "Use layer.text to add text";
    }
    TextLayer.__super__.constructor.call(this, options);
    this.style.whiteSpace = "pre-line";
    this.style.outline = "none";
  }

  TextLayer.prototype.setStyle = function(property, value, pxSuffix) {
    if (pxSuffix == null) {
      pxSuffix = false;
    }
    this.style[property] = pxSuffix ? value + "px" : value;
    this.emit("change:" + property, value);
    if (this.doAutoSize) {
      return this.calcSize();
    }
  };

  TextLayer.prototype.calcSize = function() {
    var constraints, size, sizeAffectingStyles;
    sizeAffectingStyles = {
      lineHeight: this.style["line-height"],
      fontSize: this.style["font-size"],
      fontWeight: this.style["font-weight"],
      paddingTop: this.style["padding-top"],
      paddingRight: this.style["padding-right"],
      paddingBottom: this.style["padding-bottom"],
      paddingLeft: this.style["padding-left"],
      textTransform: this.style["text-transform"],
      borderWidth: this.style["border-width"],
      letterSpacing: this.style["letter-spacing"],
      fontFamily: this.style["font-family"],
      fontStyle: this.style["font-style"],
      fontVariant: this.style["font-variant"]
    };
    constraints = {};
    if (this.doAutoSizeHeight) {
      constraints.width = this.width;
    }
    size = Utils.textSize(this.text, sizeAffectingStyles, constraints);
    if (this.style.textAlign === "right") {
      this.width = size.width;
      this.x = this.x - this.width;
    } else {
      this.width = size.width;
    }
    return this.height = size.height;
  };

  TextLayer.define("autoSize", {
    get: function() {
      return this.doAutoSize;
    },
    set: function(value) {
      this.doAutoSize = value;
      if (this.doAutoSize) {
        return this.calcSize();
      }
    }
  });

  TextLayer.define("autoSizeHeight", {
    set: function(value) {
      this.doAutoSize = value;
      this.doAutoSizeHeight = value;
      if (this.doAutoSize) {
        return this.calcSize();
      }
    }
  });

  TextLayer.define("contentEditable", {
    set: function(boolean) {
      this._element.contentEditable = boolean;
      this.ignoreEvents = !boolean;
      return this.on("input", function() {
        if (this.doAutoSize) {
          return this.calcSize();
        }
      });
    }
  });

  TextLayer.define("text", {
    get: function() {
      return this._element.textContent;
    },
    set: function(value) {
      this._element.textContent = value;
      this.emit("change:text", value);
      if (this.doAutoSize) {
        return this.calcSize();
      }
    }
  });

  TextLayer.define("fontFamily", {
    get: function() {
      return this.style.fontFamily;
    },
    set: function(value) {
      return this.setStyle("fontFamily", value);
    }
  });

  TextLayer.define("fontSize", {
    get: function() {
      return this.style.fontSize.replace("px", "");
    },
    set: function(value) {
      return this.setStyle("fontSize", value, true);
    }
  });

  TextLayer.define("lineHeight", {
    get: function() {
      return this.style.lineHeight;
    },
    set: function(value) {
      return this.setStyle("lineHeight", value);
    }
  });

  TextLayer.define("fontWeight", {
    get: function() {
      return this.style.fontWeight;
    },
    set: function(value) {
      return this.setStyle("fontWeight", value);
    }
  });

  TextLayer.define("fontStyle", {
    get: function() {
      return this.style.fontStyle;
    },
    set: function(value) {
      return this.setStyle("fontStyle", value);
    }
  });

  TextLayer.define("fontVariant", {
    get: function() {
      return this.style.fontVariant;
    },
    set: function(value) {
      return this.setStyle("fontVariant", value);
    }
  });

  TextLayer.define("padding", {
    set: function(value) {
      this.setStyle("paddingTop", value, true);
      this.setStyle("paddingRight", value, true);
      this.setStyle("paddingBottom", value, true);
      return this.setStyle("paddingLeft", value, true);
    }
  });

  TextLayer.define("paddingTop", {
    get: function() {
      return this.style.paddingTop.replace("px", "");
    },
    set: function(value) {
      return this.setStyle("paddingTop", value, true);
    }
  });

  TextLayer.define("paddingRight", {
    get: function() {
      return this.style.paddingRight.replace("px", "");
    },
    set: function(value) {
      return this.setStyle("paddingRight", value, true);
    }
  });

  TextLayer.define("paddingBottom", {
    get: function() {
      return this.style.paddingBottom.replace("px", "");
    },
    set: function(value) {
      return this.setStyle("paddingBottom", value, true);
    }
  });

  TextLayer.define("paddingLeft", {
    get: function() {
      return this.style.paddingLeft.replace("px", "");
    },
    set: function(value) {
      return this.setStyle("paddingLeft", value, true);
    }
  });

  TextLayer.define("textAlign", {
    set: function(value) {
      return this.setStyle("textAlign", value);
    }
  });

  TextLayer.define("textTransform", {
    get: function() {
      return this.style.textTransform;
    },
    set: function(value) {
      return this.setStyle("textTransform", value);
    }
  });

  TextLayer.define("letterSpacing", {
    get: function() {
      return this.style.letterSpacing.replace("px", "");
    },
    set: function(value) {
      return this.setStyle("letterSpacing", value, true);
    }
  });

  TextLayer.define("length", {
    get: function() {
      return this.text.length;
    }
  });

  return TextLayer;

})(Layer);

convertToTextLayer = function(layer) {
  var css, cssObj, importPath, t;
  t = new TextLayer({
    name: layer.name,
    frame: layer.frame,
    parent: layer.parent
  });
  cssObj = {};
  css = layer._info.metadata.css;
  css.forEach(function(rule) {
    var arr;
    if (_.includes(rule, '/*')) {
      return;
    }
    arr = rule.split(': ');
    return cssObj[arr[0]] = arr[1].replace(';', '');
  });
  t.style = cssObj;
  importPath = layer.__framerImportedFromPath;
  if (_.includes(importPath, '@2x')) {
    t.fontSize *= 2;
    t.lineHeight = (parseInt(t.lineHeight) * 2) + 'px';
    t.letterSpacing *= 2;
  }
  t.y -= (parseInt(t.lineHeight) - t.fontSize) / 2;
  t.y -= t.fontSize * 0.1;
  t.x -= t.fontSize * 0.08;
  t.width += t.fontSize * 0.5;
  t.text = layer._info.metadata.string;
  layer.destroy();
  return t;
};

Layer.prototype.convertToTextLayer = function() {
  return convertToTextLayer(this);
};

convertTextLayers = function(obj) {
  var layer, prop, results;
  results = [];
  for (prop in obj) {
    layer = obj[prop];
    if (layer._info.kind === "text") {
      results.push(obj[prop] = convertToTextLayer(layer));
    } else {
      results.push(void 0);
    }
  }
  return results;
};

Layer.prototype.frameAsTextLayer = function(properties) {
  var t;
  t = new TextLayer;
  t.frame = this.frame;
  t.superLayer = this.superLayer;
  _.extend(t, properties);
  this.destroy();
  return t;
};

exports.TextLayer = TextLayer;

exports.convertTextLayers = convertTextLayers;


},{}],"androidRipple":[function(require,module,exports){
var Pointer;

Pointer = require("Pointer").Pointer;

exports.ripple = function(event, layer) {
  var animation, color, eventCoords, pressFeedback, rippleCircle;
  eventCoords = Pointer.offset(event, layer);
  color = "black";
  animation = {
    curve: "ease-out",
    time: .4
  };
  pressFeedback = new Layer({
    superLayer: this,
    name: "pressFeedback",
    width: layer.width,
    height: layer.height,
    opacity: 0,
    backgroundColor: color
  });
  pressFeedback.states.add({
    pressed: {
      opacity: .04
    }
  });
  pressFeedback.states["switch"]("pressed", animation);
  rippleCircle = new Layer({
    superLayer: this,
    name: "rippleCircle",
    borderRadius: "50%",
    midX: eventCoords.x,
    midY: eventCoords.y,
    opacity: .16,
    backgroundColor: color
  });
  rippleCircle.states.add({
    pressed: {
      scale: layer.width / 60,
      opacity: 0
    }
  });
  rippleCircle.states["switch"]("pressed", animation);
  return Utils.delay(0.3, function() {
    pressFeedback.states.next("default", animation);
    return pressFeedback.on(Events.AnimationEnd, function() {
      rippleCircle.destroy();
      return pressFeedback.destroy();
    });
  });
};


},{"Pointer":"Pointer"}],"arcMovement":[function(require,module,exports){
exports.moveWithArc = function(layer, startPointX, startPointY, endPointX, endPointY) {
  var arc, proxy;
  arc = function(counter, layer, x1, y1, x2, y2) {
    layer.midX = startPointX - Math.sin((counter + 180) * Math.PI / 180) * (endPointX - startPointX);
    return layer.midY = endPointY - Math.cos((counter + 180) * Math.PI / 180) * (startPointY - endPointY);
  };
  proxy = new Layer({
    width: 0,
    height: 0,
    backgroundColor: "null"
  });
  proxy.states.add({
    finish: {
      x: 360
    }
  });
  proxy.states.next();
  return proxy.on("change:x", function() {
    return arc(proxy.x / 4, layer, startPointX, startPointY, endPointX, endPointY);
  });
};

exports.placeOnElipse = function(layer, centerX, centerY, angle, radiusX, radiusY) {
  layer.midX = centerX - Math.sin((angle + 180) * Math.PI / 180) * radiusX;
  return layer.midY = centerY - Math.cos((angle + 180) * Math.PI / 180) * radiusY;
};

exports.circlePoint = function(centerX, centerY, angle, radiusX, radiusY) {
  var x, y;
  x = centerX - Math.sin((angle + 180) * Math.PI / 180) * radiusX;
  y = centerY - Math.cos((angle + 180) * Math.PI / 180) * radiusY;
  return {
    x: x,
    y: y
  };
};


},{}],"distributeLayers":[function(require,module,exports){
module.exports.distributeLayers = {
  globalDefaults: {
    direction: "vertical",
    startOffset: 0
  },
  sameDistance: function(options) {
    var defaults, index, layer, offset, ref;
    defaults = {
      distance: 500
    };
    options = Object.assign({}, this.globalDefaults, defaults, options);
    this._validateOptions(options);
    offset = options.startOffset;
    ref = options.layers;
    for (index in ref) {
      layer = ref[index];
      if (options.direction === "vertical") {
        layer.y = offset;
      } else {
        layer.x = offset;
      }
      offset += options.distance;
    }
    return this._setLayerMetadata(layer, 'methodUsed', 'sameDistance');
  },
  sameMargin: function(options) {
    var defaults, index, layer, offset, ref;
    defaults = {
      margin: 10
    };
    options = Object.assign({}, this.globalDefaults, defaults, options);
    this._validateOptions(options);
    offset = options.startOffset;
    ref = options.layers;
    for (index in ref) {
      layer = ref[index];
      if (options.direction === "vertical") {
        layer.y = offset;
        offset += layer.height + options.margin;
      } else {
        layer.x = offset;
        offset += layer.width + options.margin;
      }
    }
    return this._setLayerMetadata(layer, 'methodUsed', 'sameMargin');
  },
  spaced: function(options) {
    var defaults, index, layer, offset, ref, ref1, spacing, totalArea;
    defaults = {
      max: 1000
    };
    options = Object.assign({}, this.globalDefaults, defaults, options);
    this._validateOptions(options);
    totalArea = 0;
    ref = options.layers;
    for (index in ref) {
      layer = ref[index];
      if (options.direction === "vertical") {
        totalArea += layer.height;
      } else {
        totalArea += layer.width;
      }
    }
    spacing = (options.max - totalArea) / (options.layers.length - 1);
    offset = options.startOffset;
    ref1 = options.layers;
    for (index in ref1) {
      layer = ref1[index];
      if (options.direction === "vertical") {
        layer.y = offset;
      } else {
        layer.x = offset;
      }
      offset += layer.height + spacing;
    }
    return this._setLayerMetadata(layer, 'methodUsed', 'spaced');
  },
  _validateOptions: function(options) {
    if (!options.layers) {
      throw this._error('noLayers');
    }
    if (!_.isArray(options.layers)) {
      throw this._error('layersNotArray');
    }
    if (options.layers.length === 0) {
      throw this._error('layersArrayEmpty');
    }
    if (typeof options.margin === "string") {
      throw this._error('numberAsString', options.margin);
    }
    if (typeof options.startOffset === "string") {
      throw this._error('numberAsString', options.startOffset);
    }
  },
  _error: function(id, value) {
    var err;
    err = null;
    if (id === "numberAsString") {
      err = new Error("Don't put quotation marks around numbers. " + "\"" + value + "\" should be written as " + value + ".");
    }
    if (id === "noLayers") {
      err = new Error("You didn't give distributeLayers.layers any value");
    }
    if (id === "layersNotArray") {
      err = new Error("distributeLayers.layers expects an array");
    }
    if (id === "layersArrayEmpty") {
      err = new Error("The array that you passed to distributeLayers.layers was empty");
    }
    return err;
  },
  _setLayerMetadata: function(layer, key, value) {
    if (!layer.custom) {
      layer.custom = {};
    }
    layer.custom.distributeLayers = {};
    return layer.custom.distributeLayers[key] = value;
  }
};


},{}],"firebase":[function(require,module,exports){
var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

exports.Firebase = (function(superClass) {
  var getCORSurl, request;

  extend(Firebase, superClass);

  getCORSurl = function(server, path, secret, project) {
    var url;
    switch (Utils.isWebKit()) {
      case true:
        url = "https://" + server + path + ".json?auth=" + secret + "&ns=" + project + "&sse=true";
        break;
      default:
        url = "https://" + project + ".firebaseio.com" + path + ".json?auth=" + secret;
    }
    return url;
  };

  Firebase.define("status", {
    get: function() {
      return this._status;
    }
  });

  function Firebase(options) {
    var base, base1, base2, base3;
    this.options = options != null ? options : {};
    this.projectID = (base = this.options).projectID != null ? base.projectID : base.projectID = null;
    this.secret = (base1 = this.options).secret != null ? base1.secret : base1.secret = null;
    this.server = (base2 = this.options).server != null ? base2.server : base2.server = void 0;
    this.debug = (base3 = this.options).debug != null ? base3.debug : base3.debug = false;
    if (this._status == null) {
      this._status = "disconnected";
    }
    Firebase.__super__.constructor.apply(this, arguments);
    if (this.server === void 0) {
      Utils.domLoadJSON("https://" + this.projectID + ".firebaseio.com/.settings/owner.json", function(a, server) {
        var msg;
        print(msg = "Add ______ server:" + '   "' + server + '"' + " _____ to your instance of Firebase.");
        if (this.debug) {
          return console.log("Firebase: " + msg);
        }
      });
    }
    if (this.debug) {
      console.log("Firebase: Connecting to Firebase Project '" + this.projectID + "' ... \n URL: '" + (getCORSurl(this.server, "/", this.secret, this.projectID)) + "'");
    }
    this.onChange("connection");
  }

  request = function(project, secret, path, callback, method, data, parameters, debug) {
    var url, xhttp;
    url = "https://" + project + ".firebaseio.com" + path + ".json?auth=" + secret;
    if (parameters !== void 0) {
      if (parameters.shallow) {
        url += "&shallow=true";
      }
      if (parameters.format === "export") {
        url += "&format=export";
      }
      switch (parameters.print) {
        case "pretty":
          url += "&print=pretty";
          break;
        case "silent":
          url += "&print=silent";
      }
      if (typeof parameters.download === "string") {
        url += "&download=" + parameters.download;
        window.open(url, "_self");
      }
      if (typeof parameters.orderBy === "string") {
        url += "&orderBy=" + '"' + parameters.orderBy + '"';
      }
      if (typeof parameters.limitToFirst === "number") {
        url += "&limitToFirst=" + parameters.limitToFirst;
      }
      if (typeof parameters.limitToLast === "number") {
        url += "&limitToLast=" + parameters.limitToLast;
      }
      if (typeof parameters.startAt === "number") {
        url += "&startAt=" + parameters.startAt;
      }
      if (typeof parameters.endAt === "number") {
        url += "&endAt=" + parameters.endAt;
      }
      if (typeof parameters.equalTo === "number") {
        url += "&equalTo=" + parameters.equalTo;
      }
    }
    xhttp = new XMLHttpRequest;
    if (debug) {
      console.log("Firebase: New '" + method + "'-request with data: '" + (JSON.stringify(data)) + "' \n URL: '" + url + "'");
    }
    xhttp.onreadystatechange = (function(_this) {
      return function() {
        if (parameters !== void 0) {
          if (parameters.print === "silent" || typeof parameters.download === "string") {
            return;
          }
        }
        switch (xhttp.readyState) {
          case 0:
            if (debug) {
              console.log("Firebase: Request not initialized \n URL: '" + url + "'");
            }
            break;
          case 1:
            if (debug) {
              console.log("Firebase: Server connection established \n URL: '" + url + "'");
            }
            break;
          case 2:
            if (debug) {
              console.log("Firebase: Request received \n URL: '" + url + "'");
            }
            break;
          case 3:
            if (debug) {
              console.log("Firebase: Processing request \n URL: '" + url + "'");
            }
            break;
          case 4:
            if (callback != null) {
              callback(JSON.parse(xhttp.responseText));
            }
            if (debug) {
              console.log("Firebase: Request finished, response: '" + (JSON.parse(xhttp.responseText)) + "' \n URL: '" + url + "'");
            }
        }
        if (xhttp.status === "404") {
          if (debug) {
            return console.warn("Firebase: Invalid request, page not found \n URL: '" + url + "'");
          }
        }
      };
    })(this);
    xhttp.open(method, url, true);
    xhttp.setRequestHeader("Content-type", "application/json; charset=utf-8");
    return xhttp.send(data = "" + (JSON.stringify(data)));
  };

  Firebase.prototype.get = function(path, callback, parameters) {
    return request(this.projectID, this.secret, path, callback, "GET", null, parameters, this.debug);
  };

  Firebase.prototype.put = function(path, data, callback, parameters) {
    return request(this.projectID, this.secret, path, callback, "PUT", data, parameters, this.debug);
  };

  Firebase.prototype.post = function(path, data, callback, parameters) {
    return request(this.projectID, this.secret, path, callback, "POST", data, parameters, this.debug);
  };

  Firebase.prototype.patch = function(path, data, callback, parameters) {
    return request(this.projectID, this.secret, path, callback, "PATCH", data, parameters, this.debug);
  };

  Firebase.prototype["delete"] = function(path, callback, parameters) {
    return request(this.projectID, this.secret, path, callback, "DELETE", null, parameters, this.debug);
  };

  Firebase.prototype.onChange = function(path, callback) {
    var currentStatus, source, url;
    if (path === "connection") {
      url = getCORSurl(this.server, "/", this.secret, this.projectID);
      currentStatus = "disconnected";
      source = new EventSource(url);
      source.addEventListener("open", (function(_this) {
        return function() {
          if (currentStatus === "disconnected") {
            _this._status = "connected";
            if (callback != null) {
              callback("connected");
            }
            if (_this.debug) {
              console.log("Firebase: Connection to Firebase Project '" + _this.projectID + "' established");
            }
          }
          return currentStatus = "connected";
        };
      })(this));
      return source.addEventListener("error", (function(_this) {
        return function() {
          if (currentStatus === "connected") {
            _this._status = "disconnected";
            if (callback != null) {
              callback("disconnected");
            }
            if (_this.debug) {
              console.warn("Firebase: Connection to Firebase Project '" + _this.projectID + "' closed");
            }
          }
          return currentStatus = "disconnected";
        };
      })(this));
    } else {
      url = getCORSurl(this.server, path, this.secret, this.projectID);
      source = new EventSource(url);
      if (this.debug) {
        console.log("Firebase: Listening to changes made to '" + path + "' \n URL: '" + url + "'");
      }
      source.addEventListener("put", (function(_this) {
        return function(ev) {
          if (callback != null) {
            callback(JSON.parse(ev.data).data, "put", JSON.parse(ev.data).path, _.rest(JSON.parse(ev.data).path.split("/"), 1));
          }
          if (_this.debug) {
            return console.log("Firebase: Received changes made to '" + path + "' via 'PUT': " + (JSON.parse(ev.data).data) + " \n URL: '" + url + "'");
          }
        };
      })(this));
      return source.addEventListener("patch", (function(_this) {
        return function(ev) {
          if (callback != null) {
            callback(JSON.parse(ev.data).data, "patch", JSON.parse(ev.data).path, _.rest(JSON.parse(ev.data).path.split("/"), 1));
          }
          if (_this.debug) {
            return console.log("Firebase: Received changes made to '" + path + "' via 'PATCH': " + (JSON.parse(ev.data).data) + " \n URL: '" + url + "'");
          }
        };
      })(this));
    }
  };

  return Firebase;

})(Framer.BaseClass);


},{}],"makeGradient":[function(require,module,exports){
var makeStr;

makeStr = function(obj) {
  var gradString, i, j, ref;
  gradString = obj.type + "-gradient(";
  if (obj.type === "radial" && obj.shape) {
    gradString += obj.shape + ", ";
  }
  if (obj.type === "linear" && obj.angle) {
    gradString += obj.angle + ", ";
  }
  for (i = j = 0, ref = obj.colors.length - 1; j <= ref; i = j += 1) {
    if (i === obj.colors.length - 1) {
      gradString += obj.colors[i] + "";
    } else {
      gradString += obj.colors[i] + ", ";
    }
  }
  gradString += ")";
  return gradString;
};

exports.radial = function(layer, colorArr, shape) {
  var obj;
  obj = {
    shape: shape,
    colors: colorArr,
    type: "radial"
  };
  return layer.style["background-image"] = makeStr(obj);
};

exports.linear = function(layer, colorArr, angle) {
  var obj;
  obj = {
    angle: angle,
    colors: colorArr,
    type: "linear"
  };
  return layer.style["background-image"] = makeStr(obj);
};


},{}]},{},[])
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvVXNlcnMvam9uYXMvR29vZ2xlIERyaXZlL1llc2lwZS9Gcm9udGVuZC95ZXNpcGVfMTkwOTE2LmZyYW1lci9tb2R1bGVzL1BvaW50ZXIuY29mZmVlIiwiL1VzZXJzL2pvbmFzL0dvb2dsZSBEcml2ZS9ZZXNpcGUvRnJvbnRlbmQveWVzaXBlXzE5MDkxNi5mcmFtZXIvbW9kdWxlcy9UZXh0TGF5ZXIuY29mZmVlIiwiL1VzZXJzL2pvbmFzL0dvb2dsZSBEcml2ZS9ZZXNpcGUvRnJvbnRlbmQveWVzaXBlXzE5MDkxNi5mcmFtZXIvbW9kdWxlcy9hbmRyb2lkUmlwcGxlLmNvZmZlZSIsIi9Vc2Vycy9qb25hcy9Hb29nbGUgRHJpdmUvWWVzaXBlL0Zyb250ZW5kL3llc2lwZV8xOTA5MTYuZnJhbWVyL21vZHVsZXMvYXJjTW92ZW1lbnQuY29mZmVlIiwiL1VzZXJzL2pvbmFzL0dvb2dsZSBEcml2ZS9ZZXNpcGUvRnJvbnRlbmQveWVzaXBlXzE5MDkxNi5mcmFtZXIvbW9kdWxlcy9kaXN0cmlidXRlTGF5ZXJzLmNvZmZlZSIsIi9Vc2Vycy9qb25hcy9Hb29nbGUgRHJpdmUvWWVzaXBlL0Zyb250ZW5kL3llc2lwZV8xOTA5MTYuZnJhbWVyL21vZHVsZXMvZmlyZWJhc2UuY29mZmVlIiwiL1VzZXJzL2pvbmFzL0dvb2dsZSBEcml2ZS9ZZXNpcGUvRnJvbnRlbmQveWVzaXBlXzE5MDkxNi5mcmFtZXIvbW9kdWxlcy9tYWtlR3JhZGllbnQuY29mZmVlIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiJBQUFBO0FDb0JNLE9BQU8sQ0FBQztBQUtiLE1BQUE7Ozs7RUFBQSxPQUFDLENBQUEsTUFBRCxHQUFVLFNBQUMsS0FBRCxFQUFRLEtBQVI7QUFDVCxRQUFBO0lBQUEsSUFBQSxDQUFBLENBQTZCLGVBQUEsSUFBVyxlQUF4QyxDQUFBO01BQUEsbUJBQUEsQ0FBQSxFQUFBOztJQUNBLENBQUEsR0FBSSxZ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UUFISjs7U0FNTixLQUFLLENBQUMsS0FBTSxDQUFBLGtCQUFBLENBQVosR0FBa0MsT0FBQSxDQUFRLEdBQVI7QUFQckI7O0FBU2pCLE9BQU8sQ0FBQyxNQUFSLEdBQWlCLFNBQUUsS0FBRixFQUFTLFFBQVQsRUFBbUIsS0FBbkI7QUFDYixNQUFBO0VBQUEsR0FBQSxHQUFNO0lBQ0YsS0FBQSxFQUFPLEtBREw7SUFFRixNQUFBLEVBQVEsUUFGTjtJQUdGLElBQUEsRUFBTSxRQUhKOztTQU1OLEtBQUssQ0FBQyxLQUFNLENBQUEsa0JBQUEsQ0FBWixHQUFrQyxPQUFBLENBQVEsR0FBUjtBQVByQiIsImZpbGUiOiJnZW5lcmF0ZWQuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlc0NvbnRlbnQiOlsiKGZ1bmN0aW9uIGUodCxuLHIpe2Z1bmN0aW9uIHMobyx1KXtpZighbltvXSl7aWYoIXRbb10pe3ZhciBhPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7aWYoIXUmJmEpcmV0dXJuIGEobywhMCk7aWYoaSlyZXR1cm4gaShvLCEwKTt2YXIgZj1uZXcgRXJyb3IoXCJDYW5ub3QgZmluZCBtb2R1bGUgJ1wiK28rXCInXCIpO3Rocm93IGYuY29kZT1cIk1PRFVMRV9OT1RfRk9VTkRcIixmfXZhciBsPW5bb109e2V4cG9ydHM6e319O3Rbb11bMF0uY2FsbChsLmV4cG9ydHMsZnVuY3Rpb24oZSl7dmFyIG49dFtvXVsxXVtlXTtyZXR1cm4gcyhuP246ZSl9LGwsbC5leHBvcnRzLGUsdCxuLHIpfXJldHVybiBuW29dLmV4cG9ydHN9dmFyIGk9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtmb3IodmFyIG89MDtvPHIubGVuZ3RoO28rKylzKHJbb10pO3JldHVybiBzfSkiLCIjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyNcbiMgQ3JlYXRlZCBieSBKb3JkYW4gUm9iZXJ0IERvYnNvbiBvbiAxNCBBdWd1c3QgMjAxNVxuIyBcbiMgVXNlIHRvIG5vcm1hbGl6ZSBzY3JlZW4gJiBvZmZzZXQgeCx5IHZhbHVlcyBmcm9tIGNsaWNrIG9yIHRvdWNoIGV2ZW50cy5cbiNcbiMgVG8gR2V0IFN0YXJ0ZWQuLi5cbiNcbiMgMS4gUGxhY2UgdGhpcyBmaWxlIGluIEZyYW1lciBTdHVkaW8gbW9kdWxlcyBkaXJlY3RvcnlcbiNcbiMgMi4gSW4geW91ciBwcm9qZWN0IGluY2x1ZGU6XG4jICAgICB7UG9pbnRlcn0gPSByZXF1aXJlIFwiUG9pbnRlclwiXG4jXG4jIDMuIEZvciBzY3JlZW4gY29vcmRpbmF0ZXM6IFxuIyAgICAgYnRuLm9uIEV2ZW50cy5DbGljaywgKGV2ZW50LCBsYXllcikgLT4gcHJpbnQgUG9pbnRlci5zY3JlZW4oZXZlbnQsIGxheWVyKVxuIyBcbiMgNC4gRm9yIGxheWVyIG9mZnNldCBjb29yZGluYXRlczogXG4jICAgICBidG4ub24gRXZlbnRzLkNsaWNrLCAoZXZlbnQsIGxheWVyKSAtPiBwcmludCBQb2ludGVyLm9mZnNldChldmVudCwgbGF5ZXIpXG4jXG4jIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyNcblxuY2xhc3MgZXhwb3J0cy5Qb2ludGVyXG5cblx0IyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjXG5cdCMgUHVibGljIE1ldGhvZHMgIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI1xuXG5cdEBzY3JlZW4gPSAoZXZlbnQsIGxheWVyKSAtPlxuXHRcdHNjcmVlbkFyZ3VtZW50RXJyb3IoKSB1bmxlc3MgZXZlbnQ/IGFuZCBsYXllcj9cblx0XHRlID0gb2Zmc2V0Q29vcmRzIGV2ZW50XG5cdFx0aWYgZS54IGFuZCBlLnlcblx0XHRcdCMgTW91c2UgRXZlbnRcblx0XHRcdHNjcmVlbkNvb3JkcyA9IGxheWVyLnNjcmVlbkZyYW1lXG5cdFx0XHRlLnggKz0gc2NyZWVuQ29vcmRzLnhcblx0XHRcdGUueSArPSBzY3JlZW5Db29yZHMueVxuXHRcdGVsc2Vcblx0XHRcdCMgVG91Y2ggRXZlbnRcblx0XHRcdGUgPSBjbGllbnRDb29yZHMgZXZlbnRcblx0XHRyZXR1cm4gZVxuXHRcdFx0XG5cdEBvZmZzZXQgPSAoZXZlbnQsIGxheWVyKSAtPlxuXHRcdG9mZnNldEFyZ3VtZW50RXJyb3IoKSB1bmxlc3MgZXZlbnQ/IGFuZCBsYXllcj9cblx0XHRlID0gb2Zmc2V0Q29vcmRzIGV2ZW50XG5cdFx0dW5sZXNzIGUueD8gYW5kIGUueT9cblx0XHRcdCMgVG91Y2ggRXZlbnRcblx0XHRcdGUgPSBjbGllbnRDb29yZHMgZXZlbnRcblx0XHRcdHRhcmdldFNjcmVlbkNvb3JkcyA9IGxheWVyLnNjcmVlbkZyYW1lXG5cdFx0XHRlLnggLT0gdGFyZ2V0U2NyZWVuQ29vcmRzLnhcblx0XHRcdGUueSAtPSB0YXJnZXRTY3JlZW5Db29yZHMueVxuXHRcdHJldHVybiBlXG5cdFxuXHQjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyNcblx0IyBQcml2YXRlIEhlbHBlciBNZXRob2RzICMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjXG5cdFxuXHRvZmZzZXRDb29yZHMgPSAoZXYpICAtPiBlID0gRXZlbnRzLnRvdWNoRXZlbnQgZXY7IHJldHVybiBjb29yZHMgZS5vZmZzZXRYLCBlLm9mZnNldFlcblx0Y2xpZW50Q29vcmRzID0gKGV2KSAgLT4gZSA9IEV2ZW50cy50b3VjaEV2ZW50IGV2OyByZXR1cm4gY29vcmRzIGUuY2xpZW50WCwgZS5jbGllbnRZXG5cdGNvb3JkcyAgICAgICA9ICh4LHkpIC0+IHJldHVybiB4OngsIHk6eVxuXHRcblx0IyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjXG5cdCMgRXJyb3IgSGFuZGxlciBNZXRob2RzICMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI1xuXHRcblx0c2NyZWVuQXJndW1lbnRFcnJvciA9IC0+XG5cdFx0ZXJyb3IgbnVsbFxuXHRcdGNvbnNvbGUuZXJyb3IgXCJcIlwiXG5cdFx0XHRQb2ludGVyLnNjcmVlbigpIEVycm9yOiBZb3UgbXVzdCBwYXNzIGV2ZW50ICYgbGF5ZXIgYXJndW1lbnRzLiBcXG5cblx0XHRcdEV4YW1wbGU6IGxheWVyLm9uIEV2ZW50cy5Ub3VjaFN0YXJ0LChldmVudCxsYXllcikgLT4gUG9pbnRlci5zY3JlZW4oZXZlbnQsIGxheWVyKVwiXCJcIlxuXHRcdFx0XG5cdG9mZnNldEFyZ3VtZW50RXJyb3IgPSAtPlxuXHRcdGVycm9yIG51bGxcblx0XHRjb25zb2xlLmVycm9yIFwiXCJcIlxuXHRcdFx0UG9pbnRlci5vZmZzZXQoKSBFcnJvcjogWW91IG11c3QgcGFzcyBldmVudCAmIGxheWVyIGFyZ3VtZW50cy4gXFxuXG5cdFx0XHRFeGFtcGxlOiBsYXllci5vbiBFdmVudHMuVG91Y2hTdGFydCwoZXZlbnQsbGF5ZXIpIC0+IFBvaW50ZXIub2Zmc2V0KGV2ZW50LCBsYXllcilcIlwiXCIiLCJjbGFzcyBUZXh0TGF5ZXIgZXh0ZW5kcyBMYXllclxuXHRcdFxuXHRjb25zdHJ1Y3RvcjogKG9wdGlvbnM9e30pIC0+XG5cdFx0QGRvQXV0b1NpemUgPSBmYWxzZVxuXHRcdEBkb0F1dG9TaXplSGVpZ2h0ID0gZmFsc2Vcblx0XHRvcHRpb25zLmJhY2tncm91bmRDb2xvciA/PSBpZiBvcHRpb25zLnNldHVwIHRoZW4gXCJoc2xhKDYwLCA5MCUsIDQ3JSwgLjQpXCIgZWxzZSBcInRyYW5zcGFyZW50XCJcblx0XHRvcHRpb25zLmNvbG9yID89IFwicmVkXCJcblx0XHRvcHRpb25zLmxpbmVIZWlnaHQgPz0gMS4yNVxuXHRcdG9wdGlvbnMuZm9udEZhbWlseSA/PSBcIkhlbHZldGljYVwiXG5cdFx0b3B0aW9ucy5mb250U2l6ZSA/PSAyMFxuXHRcdG9wdGlvbnMudGV4dCA/PSBcIlVzZSBsYXllci50ZXh0IHRvIGFkZCB0ZXh0XCJcblx0XHRzdXBlciBvcHRpb25zXG5cdFx0QHN0eWxlLndoaXRlU3BhY2UgPSBcInByZS1saW5lXCIgIyBhbGxvdyBcXG4gaW4gLnRleHRcblx0XHRAc3R5bGUub3V0bGluZSA9IFwibm9uZVwiICMgbm8gYm9yZGVyIHdoZW4gc2VsZWN0ZWRcblx0XHRcblx0c2V0U3R5bGU6IChwcm9wZXJ0eSwgdmFsdWUsIHB4U3VmZml4ID0gZmFsc2UpIC0+XG5cdFx0QHN0eWxlW3Byb3BlcnR5XSA9IGlmIHB4U3VmZml4IHRoZW4gdmFsdWUrXCJweFwiIGVsc2UgdmFsdWVcblx0XHRAZW1pdChcImNoYW5nZToje3Byb3BlcnR5fVwiLCB2YWx1ZSlcblx0XHRpZiBAZG9BdXRvU2l6ZSB0aGVuIEBjYWxjU2l6ZSgpXG5cdFx0XG5cdGNhbGNTaXplOiAtPlxuXHRcdHNpemVBZmZlY3RpbmdTdHlsZXMgPVxuXHRcdFx0bGluZUhlaWdodDogQHN0eWxlW1wibGluZS1oZWlnaHRcIl1cblx0XHRcdGZvbnRTaXplOiBAc3R5bGVbXCJmb250LXNpemVcIl1cblx0XHRcdGZvbnRXZWlnaHQ6IEBzdHlsZVtcImZvbnQtd2VpZ2h0XCJdXG5cdFx0XHRwYWRkaW5nVG9wOiBAc3R5bGVbXCJwYWRkaW5nLXRvcFwiXVxuXHRcdFx0cGFkZGluZ1JpZ2h0OiBAc3R5bGVbXCJwYWRkaW5nLXJpZ2h0XCJdXG5cdFx0XHRwYWRkaW5nQm90dG9tOiBAc3R5bGVbXCJwYWRkaW5nLWJvdHRvbVwiXVxuXHRcdFx0cGFkZGluZ0xlZnQ6IEBzdHlsZVtcInBhZGRpbmctbGVmdFwiXVxuXHRcdFx0dGV4dFRyYW5zZm9ybTogQHN0eWxlW1widGV4dC10cmFuc2Zvcm1cIl1cblx0XHRcdGJvcmRlcldpZHRoOiBAc3R5bGVbXCJib3JkZXItd2lkdGhcIl1cblx0XHRcdGxldHRlclNwYWNpbmc6IEBzdHlsZVtcImxldHRlci1zcGFjaW5nXCJdXG5cdFx0XHRmb250RmFtaWx5OiBAc3R5bGVbXCJmb250LWZhbWlseVwiXVxuXHRcdFx0Zm9udFN0eWxlOiBAc3R5bGVbXCJmb250LXN0eWxlXCJdXG5cdFx0XHRmb250VmFyaWFudDogQHN0eWxlW1wiZm9udC12YXJpYW50XCJdXG5cdFx0Y29uc3RyYWludHMgPSB7fVxuXHRcdGlmIEBkb0F1dG9TaXplSGVpZ2h0IHRoZW4gY29uc3RyYWludHMud2lkdGggPSBAd2lkdGhcblx0XHRzaXplID0gVXRpbHMudGV4dFNpemUgQHRleHQsIHNpemVBZmZlY3RpbmdTdHlsZXMsIGNvbnN0cmFpbnRzXG5cdFx0aWYgQHN0eWxlLnRleHRBbGlnbiBpcyBcInJpZ2h0XCJcblx0XHRcdEB3aWR0aCA9IHNpemUud2lkdGhcblx0XHRcdEB4ID0gQHgtQHdpZHRoXG5cdFx0ZWxzZVxuXHRcdFx0QHdpZHRoID0gc2l6ZS53aWR0aFxuXHRcdEBoZWlnaHQgPSBzaXplLmhlaWdodFxuXG5cdEBkZWZpbmUgXCJhdXRvU2l6ZVwiLFxuXHRcdGdldDogLT4gQGRvQXV0b1NpemVcblx0XHRzZXQ6ICh2YWx1ZSkgLT4gXG5cdFx0XHRAZG9BdXRvU2l6ZSA9IHZhbHVlXG5cdFx0XHRpZiBAZG9BdXRvU2l6ZSB0aGVuIEBjYWxjU2l6ZSgpXG5cdEBkZWZpbmUgXCJhdXRvU2l6ZUhlaWdodFwiLFxuXHRcdHNldDogKHZhbHVlKSAtPiBcblx0XHRcdEBkb0F1dG9TaXplID0gdmFsdWVcblx0XHRcdEBkb0F1dG9TaXplSGVpZ2h0ID0gdmFsdWVcblx0XHRcdGlmIEBkb0F1dG9TaXplIHRoZW4gQGNhbGNTaXplKClcblx0QGRlZmluZSBcImNvbnRlbnRFZGl0YWJsZVwiLFxuXHRcdHNldDogKGJvb2xlYW4pIC0+XG5cdFx0XHRAX2VsZW1lbnQuY29udGVudEVkaXRhYmxlID0gYm9vbGVhblxuXHRcdFx0QGlnbm9yZUV2ZW50cyA9ICFib29sZWFuXG5cdFx0XHRAb24gXCJpbnB1dFwiLCAtPiBAY2FsY1NpemUoKSBpZiBAZG9BdXRvU2l6ZVxuXHRAZGVmaW5lIFwidGV4dFwiLFxuXHRcdGdldDogLT4gQF9lbGVtZW50LnRleHRDb250ZW50XG5cdFx0c2V0OiAodmFsdWUpIC0+XG5cdFx0XHRAX2VsZW1lbnQudGV4dENvbnRlbnQgPSB2YWx1ZVxuXHRcdFx0QGVtaXQoXCJjaGFuZ2U6dGV4dFwiLCB2YWx1ZSlcblx0XHRcdGlmIEBkb0F1dG9TaXplIHRoZW4gQGNhbGNTaXplKClcblx0QGRlZmluZSBcImZvbnRGYW1pbHlcIiwgXG5cdFx0Z2V0OiAtPiBAc3R5bGUuZm9udEZhbWlseVxuXHRcdHNldDogKHZhbHVlKSAtPiBAc2V0U3R5bGUoXCJmb250RmFtaWx5XCIsIHZhbHVlKVxuXHRAZGVmaW5lIFwiZm9udFNpemVcIiwgXG5cdFx0Z2V0OiAtPiBAc3R5bGUuZm9udFNpemUucmVwbGFjZShcInB4XCIsXCJcIilcblx0XHRzZXQ6ICh2YWx1ZSkgLT4gQHNldFN0eWxlKFwiZm9udFNpemVcIiwgdmFsdWUsIHRydWUpXG5cdEBkZWZpbmUgXCJsaW5lSGVpZ2h0XCIsIFxuXHRcdGdldDogLT4gQHN0eWxlLmxpbmVIZWlnaHQgXG5cdFx0c2V0OiAodmFsdWUpIC0+IEBzZXRTdHlsZShcImxpbmVIZWlnaHRcIiwgdmFsdWUpXG5cdEBkZWZpbmUgXCJmb250V2VpZ2h0XCIsIFxuXHRcdGdldDogLT4gQHN0eWxlLmZvbnRXZWlnaHQgXG5cdFx0c2V0OiAodmFsdWUpIC0+IEBzZXRTdHlsZShcImZvbnRXZWlnaHRcIiwgdmFsdWUpXG5cdEBkZWZpbmUgXCJmb250U3R5bGVcIiwgXG5cdFx0Z2V0OiAtPiBAc3R5bGUuZm9udFN0eWxlXG5cdFx0c2V0OiAodmFsdWUpIC0+IEBzZXRTdHlsZShcImZvbnRTdHlsZVwiLCB2YWx1ZSlcblx0QGRlZmluZSBcImZvbnRWYXJpYW50XCIsIFxuXHRcdGdldDogLT4gQHN0eWxlLmZvbnRWYXJpYW50XG5cdFx0c2V0OiAodmFsdWUpIC0+IEBzZXRTdHlsZShcImZvbnRWYXJpYW50XCIsIHZhbHVlKVxuXHRAZGVmaW5lIFwicGFkZGluZ1wiLFxuXHRcdHNldDogKHZhbHVlKSAtPiBcblx0XHRcdEBzZXRTdHlsZShcInBhZGRpbmdUb3BcIiwgdmFsdWUsIHRydWUpXG5cdFx0XHRAc2V0U3R5bGUoXCJwYWRkaW5nUmlnaHRcIiwgdmFsdWUsIHRydWUpXG5cdFx0XHRAc2V0U3R5bGUoXCJwYWRkaW5nQm90dG9tXCIsIHZhbHVlLCB0cnVlKVxuXHRcdFx0QHNldFN0eWxlKFwicGFkZGluZ0xlZnRcIiwgdmFsdWUsIHRydWUpXG5cdEBkZWZpbmUgXCJwYWRkaW5nVG9wXCIsIFxuXHRcdGdldDogLT4gQHN0eWxlLnBhZGRpbmdUb3AucmVwbGFjZShcInB4XCIsXCJcIilcblx0XHRzZXQ6ICh2YWx1ZSkgLT4gQHNldFN0eWxlKFwicGFkZGluZ1RvcFwiLCB2YWx1ZSwgdHJ1ZSlcblx0QGRlZmluZSBcInBhZGRpbmdSaWdodFwiLCBcblx0XHRnZXQ6IC0+IEBzdHlsZS5wYWRkaW5nUmlnaHQucmVwbGFjZShcInB4XCIsXCJcIilcblx0XHRzZXQ6ICh2YWx1ZSkgLT4gQHNldFN0eWxlKFwicGFkZGluZ1JpZ2h0XCIsIHZhbHVlLCB0cnVlKVxuXHRAZGVmaW5lIFwicGFkZGluZ0JvdHRvbVwiLCBcblx0XHRnZXQ6IC0+IEBzdHlsZS5wYWRkaW5nQm90dG9tLnJlcGxhY2UoXCJweFwiLFwiXCIpXG5cdFx0c2V0OiAodmFsdWUpIC0+IEBzZXRTdHlsZShcInBhZGRpbmdCb3R0b21cIiwgdmFsdWUsIHRydWUpXG5cdEBkZWZpbmUgXCJwYWRkaW5nTGVmdFwiLFxuXHRcdGdldDogLT4gQHN0eWxlLnBhZGRpbmdMZWZ0LnJlcGxhY2UoXCJweFwiLFwiXCIpXG5cdFx0c2V0OiAodmFsdWUpIC0+IEBzZXRTdHlsZShcInBhZGRpbmdMZWZ0XCIsIHZhbHVlLCB0cnVlKVxuXHRAZGVmaW5lIFwidGV4dEFsaWduXCIsXG5cdFx0c2V0OiAodmFsdWUpIC0+IEBzZXRTdHlsZShcInRleHRBbGlnblwiLCB2YWx1ZSlcblx0QGRlZmluZSBcInRleHRUcmFuc2Zvcm1cIiwgXG5cdFx0Z2V0OiAtPiBAc3R5bGUudGV4dFRyYW5zZm9ybSBcblx0XHRzZXQ6ICh2YWx1ZSkgLT4gQHNldFN0eWxlKFwidGV4dFRyYW5zZm9ybVwiLCB2YWx1ZSlcblx0QGRlZmluZSBcImxldHRlclNwYWNpbmdcIiwgXG5cdFx0Z2V0OiAtPiBAc3R5bGUubGV0dGVyU3BhY2luZy5yZXBsYWNlKFwicHhcIixcIlwiKVxuXHRcdHNldDogKHZhbHVlKSAtPiBAc2V0U3R5bGUoXCJsZXR0ZXJTcGFjaW5nXCIsIHZhbHVlLCB0cnVlKVxuXHRAZGVmaW5lIFwibGVuZ3RoXCIsIFxuXHRcdGdldDogLT4gQHRleHQubGVuZ3RoXG5cbmNvbnZlcnRUb1RleHRMYXllciA9IChsYXllcikgLT5cblx0dCA9IG5ldyBUZXh0TGF5ZXJcblx0XHRuYW1lOiBsYXllci5uYW1lXG5cdFx0ZnJhbWU6IGxheWVyLmZyYW1lXG5cdFx0cGFyZW50OiBsYXllci5wYXJlbnRcblx0XG5cdGNzc09iaiA9IHt9XG5cdGNzcyA9IGxheWVyLl9pbmZvLm1ldGFkYXRhLmNzc1xuXHRjc3MuZm9yRWFjaCAocnVsZSkgLT5cblx0XHRyZXR1cm4gaWYgXy5pbmNsdWRlcyBydWxlLCAnLyonXG5cdFx0YXJyID0gcnVsZS5zcGxpdCgnOiAnKVxuXHRcdGNzc09ialthcnJbMF1dID0gYXJyWzFdLnJlcGxhY2UoJzsnLCcnKVxuXHR0LnN0eWxlID0gY3NzT2JqXG5cdFxuXHRpbXBvcnRQYXRoID0gbGF5ZXIuX19mcmFtZXJJbXBvcnRlZEZyb21QYXRoXG5cdGlmIF8uaW5jbHVkZXMgaW1wb3J0UGF0aCwgJ0AyeCdcblx0XHR0LmZvbnRTaXplICo9IDJcblx0XHR0LmxpbmVIZWlnaHQgPSAocGFyc2VJbnQodC5saW5lSGVpZ2h0KSoyKSsncHgnXG5cdFx0dC5sZXR0ZXJTcGFjaW5nICo9IDJcblx0XHRcdFx0XHRcblx0dC55IC09IChwYXJzZUludCh0LmxpbmVIZWlnaHQpLXQuZm9udFNpemUpLzIgIyBjb21wZW5zYXRlIGZvciBob3cgQ1NTIGhhbmRsZXMgbGluZSBoZWlnaHRcblx0dC55IC09IHQuZm9udFNpemUgKiAwLjEgIyBza2V0Y2ggcGFkZGluZ1xuXHR0LnggLT0gdC5mb250U2l6ZSAqIDAuMDggIyBza2V0Y2ggcGFkZGluZ1xuXHR0LndpZHRoICs9IHQuZm9udFNpemUgKiAwLjUgIyBza2V0Y2ggcGFkZGluZ1xuXG5cdHQudGV4dCA9IGxheWVyLl9pbmZvLm1ldGFkYXRhLnN0cmluZ1xuXHRsYXllci5kZXN0cm95KClcblx0cmV0dXJuIHRcblxuTGF5ZXI6OmNvbnZlcnRUb1RleHRMYXllciA9IC0+IGNvbnZlcnRUb1RleHRMYXllcihAKVxuXG5jb252ZXJ0VGV4dExheWVycyA9IChvYmopIC0+XG5cdGZvciBwcm9wLGxheWVyIG9mIG9ialxuXHRcdGlmIGxheWVyLl9pbmZvLmtpbmQgaXMgXCJ0ZXh0XCJcblx0XHRcdG9ialtwcm9wXSA9IGNvbnZlcnRUb1RleHRMYXllcihsYXllcilcblxuIyBCYWNrd2FyZHMgY29tcGFiaWxpdHkuIFJlcGxhY2VkIGJ5IGNvbnZlcnRUb1RleHRMYXllcigpXG5MYXllcjo6ZnJhbWVBc1RleHRMYXllciA9IChwcm9wZXJ0aWVzKSAtPlxuICAgIHQgPSBuZXcgVGV4dExheWVyXG4gICAgdC5mcmFtZSA9IEBmcmFtZVxuICAgIHQuc3VwZXJMYXllciA9IEBzdXBlckxheWVyXG4gICAgXy5leHRlbmQgdCxwcm9wZXJ0aWVzXG4gICAgQGRlc3Ryb3koKVxuICAgIHRcblxuZXhwb3J0cy5UZXh0TGF5ZXIgPSBUZXh0TGF5ZXJcbmV4cG9ydHMuY29udmVydFRleHRMYXllcnMgPSBjb252ZXJ0VGV4dExheWVyc1xuIiwiIyBNb2R1bGUgY3JlYXRlZCBieSBBYXJvbiBKYW1lcyB8IE5vdmVtYmVyIDI0dGgsIDIwMTVcbiNcbiMgUG9pbnRlciBNb2R1bGUgYnkgSm9yZGFuIERvYnNvbiBpcyByZXF1aXJlZCBmb3IgdGhpcyBtb2R1bGVcbiMgSW5zdGFsbCB0aGlzIG1vZHVsZSBmaXJzdCBoZXJlOiBodHRwOi8vYml0Lmx5LzFsZ21OcFRcbiNcbiMgQWRkIHRoZSBmb2xsb3dpbmcgbGluZSBhdCB0aGUgdG9wIG9mIHlvdXIgcHJvamVjdCB0byBhY2Nlc3MgdGhpcyBtb2R1bGU6XG4jIGFuZHJvaWQgPSByZXF1aXJlIFwiYW5kcm9pZFJpcHBsZVwiXG4jXG4jIFRvIGFkZCByaXBwbGUgdG8gbGF5ZXIsIHVzZSB0aGlzIGxpbmUgb2YgY29kZTpcbiMgbGF5ZXJOYW1lLm9uKEV2ZW50cy5DbGljaywgYW5kcm9pZC5yaXBwbGUpXG4jIFJlcGxhY2UgbGF5ZXJOYW1lIHdpdGggdGhlIG5hbWUgb2YgeW91ciBsYXllclxuI1xuIyBBdmFpbGFibGUgb3B0aW9uczpcbiMgWW91IGNhbiB1c2UgYW55IEV2ZW50IHdpdGggdGhpcyBtb2R1bGVcblxue1BvaW50ZXJ9ID0gcmVxdWlyZSBcIlBvaW50ZXJcIlxuXG4jIGNyZWF0ZSByaXBwbGUgZnVuY3Rpb25cbmV4cG9ydHMucmlwcGxlID0gKGV2ZW50LCBsYXllcikgLT5cblx0ZXZlbnRDb29yZHMgPSBQb2ludGVyLm9mZnNldChldmVudCwgbGF5ZXIpXG5cblx0IyBDaGFuZ2UgY29sb3Igb2YgcmlwcGxlXG5cdGNvbG9yID0gXCJibGFja1wiXG5cdGFuaW1hdGlvbiA9IGN1cnZlOiBcImVhc2Utb3V0XCIsIHRpbWU6IC40XG5cblx0IyBDcmVhdGUgbGF5ZXJzIG9uIENsaWNrXG5cdHByZXNzRmVlZGJhY2sgPSBuZXcgTGF5ZXJcblx0XHRzdXBlckxheWVyOiBAXG5cdFx0bmFtZTogXCJwcmVzc0ZlZWRiYWNrXCJcblx0XHR3aWR0aDogbGF5ZXIud2lkdGhcblx0XHRoZWlnaHQ6IGxheWVyLmhlaWdodFxuXHRcdG9wYWNpdHk6IDBcblx0XHRiYWNrZ3JvdW5kQ29sb3I6IGNvbG9yXG5cdHByZXNzRmVlZGJhY2suc3RhdGVzLmFkZFxuXHRcdHByZXNzZWQ6IG9wYWNpdHk6IC4wNFxuXHRwcmVzc0ZlZWRiYWNrLnN0YXRlcy5zd2l0Y2goXCJwcmVzc2VkXCIsIGFuaW1hdGlvbilcblxuXHRyaXBwbGVDaXJjbGUgPSBuZXcgTGF5ZXJcblx0XHRzdXBlckxheWVyOiBAXG5cdFx0bmFtZTogXCJyaXBwbGVDaXJjbGVcIlxuXHRcdGJvcmRlclJhZGl1czogXCI1MCVcIlxuXHRcdG1pZFg6IGV2ZW50Q29vcmRzLnhcblx0XHRtaWRZOiBldmVudENvb3Jkcy55XG5cdFx0b3BhY2l0eTogLjE2XG5cdFx0YmFja2dyb3VuZENvbG9yOiBjb2xvclxuXHRyaXBwbGVDaXJjbGUuc3RhdGVzLmFkZFxuXHRcdHByZXNzZWQ6IHNjYWxlOiBsYXllci53aWR0aCAvIDYwLCBvcGFjaXR5OiAwLFxuXHRyaXBwbGVDaXJjbGUuc3RhdGVzLnN3aXRjaChcInByZXNzZWRcIiwgYW5pbWF0aW9uKVxuXG5cdCMgRGVzdHJveSBsYXllcnMgYWZ0ZXIgQ2xpY2tcblx0VXRpbHMuZGVsYXkgMC4zLCAtPlxuXHRcdHByZXNzRmVlZGJhY2suc3RhdGVzLm5leHQoXCJkZWZhdWx0XCIsIGFuaW1hdGlvbilcblx0XHRwcmVzc0ZlZWRiYWNrLm9uIEV2ZW50cy5BbmltYXRpb25FbmQsIC0+XG5cdFx0XHRyaXBwbGVDaXJjbGUuZGVzdHJveSgpXG5cdFx0XHRwcmVzc0ZlZWRiYWNrLmRlc3Ryb3koKVxuIiwiI2F1dGhvciBTZXJnaXkgVm9yb25vdiB0d2l0dGVyLmNvbS9tYW1leml0byBkcmliYmJsZS5jb20vbWFtZXppdG9cbiNkb25lIGZvciBGcmFtZXIgTG9uZG9uIGZyYW1lcmxvbmRvbi5jb21cblxuXG5leHBvcnRzLm1vdmVXaXRoQXJjPShsYXllciwgc3RhcnRQb2ludFgsIHN0YXJ0UG9pbnRZLCBlbmRQb2ludFgsIGVuZFBvaW50WSktPlxuXHRhcmM9KGNvdW50ZXIsbGF5ZXIsIHgxLCB5MSwgeDIsIHkyKS0+XG5cdFx0bGF5ZXIubWlkWD1zdGFydFBvaW50WC1NYXRoLnNpbigoY291bnRlcisxODApICAqIE1hdGguUEkgLyAxODApKihlbmRQb2ludFgtc3RhcnRQb2ludFgpXG5cdFx0bGF5ZXIubWlkWT1lbmRQb2ludFktTWF0aC5jb3MoKGNvdW50ZXIrMTgwKSAgKiBNYXRoLlBJIC8gMTgwKSooc3RhcnRQb2ludFktZW5kUG9pbnRZKVxuXG5cdHByb3h5ID0gbmV3IExheWVyXG5cdFx0d2lkdGg6IDBcblx0XHRoZWlnaHQ6IDBcblx0XHRiYWNrZ3JvdW5kQ29sb3I6IFwibnVsbFwiXG5cblx0cHJveHkuc3RhdGVzLmFkZFxuXHRcdGZpbmlzaDpcblx0XHRcdHg6IDM2MFxuXG5cdHByb3h5LnN0YXRlcy5uZXh0KClcblxuXHRwcm94eS5vbiBcImNoYW5nZTp4XCIsIC0+XG5cdFx0YXJjIHByb3h5LngvNCwgbGF5ZXIsIHN0YXJ0UG9pbnRYLCBzdGFydFBvaW50WSwgZW5kUG9pbnRYLCBlbmRQb2ludFlcblxuZXhwb3J0cy5wbGFjZU9uRWxpcHNlPShsYXllciwgY2VudGVyWCwgY2VudGVyWSwgYW5nbGUsIHJhZGl1c1gsIHJhZGl1c1kpLT5cblx0bGF5ZXIubWlkWD1jZW50ZXJYLU1hdGguc2luKChhbmdsZSsxODApICAqIE1hdGguUEkgLyAxODApKnJhZGl1c1hcblx0bGF5ZXIubWlkWT1jZW50ZXJZLU1hdGguY29zKChhbmdsZSsxODApICAqIE1hdGguUEkgLyAxODApKnJhZGl1c1lcblxuZXhwb3J0cy5jaXJjbGVQb2ludD0oY2VudGVyWCwgY2VudGVyWSwgYW5nbGUsIHJhZGl1c1gsIHJhZGl1c1kpLT5cblx0XHR4PWNlbnRlclgtTWF0aC5zaW4oKGFuZ2xlKzE4MCkgICogTWF0aC5QSSAvIDE4MCkqcmFkaXVzWFxuXHRcdHk9Y2VudGVyWS1NYXRoLmNvcygoYW5nbGUrMTgwKSAgKiBNYXRoLlBJIC8gMTgwKSpyYWRpdXNZXG5cdFx0cmV0dXJuIHg6eCwgeTp5XG4iLCJtb2R1bGUuZXhwb3J0cy5kaXN0cmlidXRlTGF5ZXJzID1cblxuXHQjIERlZmF1bHRzIHVzZWQgYnkgZXZlcnkgcHVibGljIG1ldGhvZFxuXHRnbG9iYWxEZWZhdWx0czpcblx0XHRkaXJlY3Rpb246IFwidmVydGljYWxcIlxuXHRcdHN0YXJ0T2Zmc2V0OiAwXG5cblx0IyBBbGwgbGF5ZXJzIGhhdmUgdGhlIHNhbWUgZGlzdGFuY2UgZnJvbSBlYWNob3RoZXIuIDUwLCAxMDAsIDE1MCwgMjAwIGV0Yy5cblx0c2FtZURpc3RhbmNlOiAob3B0aW9ucykgLT5cblxuXHRcdCMgQXJndW1lbnRzIHRoYXQgYXJlIHVuaXF1ZSB0byB0aGlzIG1ldGhvZFxuXHRcdGRlZmF1bHRzID1cblx0XHRcdGRpc3RhbmNlOiA1MDBcblxuXHRcdCMgU2V0IHVwIG9wdGlvbnMgYW5kIHZhbGlkYXRlIHByb3BlcnRpZXNcblx0XHRvcHRpb25zID0gT2JqZWN0LmFzc2lnbih7fSwgdGhpcy5nbG9iYWxEZWZhdWx0cywgZGVmYXVsdHMsIG9wdGlvbnMpXG5cdFx0dGhpcy5fdmFsaWRhdGVPcHRpb25zKG9wdGlvbnMpXG5cblx0XHQjIExvb3AgdGhyb3VnaCBhbGwgbGF5ZXJzIGFuZCBwb3NpdGlvbiB0aGVtXG5cdFx0b2Zmc2V0ID0gb3B0aW9ucy5zdGFydE9mZnNldFxuXHRcdGZvciBpbmRleCwgbGF5ZXIgb2Ygb3B0aW9ucy5sYXllcnNcblx0XHRcdGlmIG9wdGlvbnMuZGlyZWN0aW9uID09IFwidmVydGljYWxcIlxuXHRcdFx0XHRsYXllci55ID0gb2Zmc2V0XG5cdFx0XHRlbHNlXG5cdFx0XHRcdGxheWVyLnggPSBvZmZzZXRcblx0XHRcdG9mZnNldCArPSBvcHRpb25zLmRpc3RhbmNlXG5cblx0XHQjIFJlbWVtYmVyIHdoaWNoIG1ldGhvZCB3YXMgdXNlZFxuXHRcdHRoaXMuX3NldExheWVyTWV0YWRhdGEobGF5ZXIsICdtZXRob2RVc2VkJywgJ3NhbWVEaXN0YW5jZScpXG5cblx0IyBMYXllcnMgZm9sbG93IG9uZSBhbm90aGVyLiBUaGV5IGFyZSBzcGFjZWQgd2l0aCB0aGUgc2FtZSBtYXJnaW4uXG5cdHNhbWVNYXJnaW46IChvcHRpb25zKSAtPlxuXG5cdFx0IyBBcmd1bWVudHMgdGhhdCBhcmUgdW5pcXVlIHRvIHRoaXMgbWV0aG9kXG5cdFx0ZGVmYXVsdHMgPVxuXHRcdFx0bWFyZ2luOiAxMFxuXG5cdFx0IyBTZXQgdXAgb3B0aW9ucyBhbmQgdmFsaWRhdGUgcHJvcGVydGllc1xuXHRcdG9wdGlvbnMgPSBPYmplY3QuYXNzaWduKHt9LCB0aGlzLmdsb2JhbERlZmF1bHRzLCBkZWZhdWx0cywgb3B0aW9ucylcblx0XHR0aGlzLl92YWxpZGF0ZU9wdGlvbnMob3B0aW9ucylcblxuXHRcdCMgTG9vcCB0aHJvdWdoIGFsbCBsYXllcnMgYW5kIHBvc2l0aW9uIHRoZW1cblx0XHRvZmZzZXQgPSBvcHRpb25zLnN0YXJ0T2Zmc2V0XG5cdFx0Zm9yIGluZGV4LCBsYXllciBvZiBvcHRpb25zLmxheWVyc1xuXHRcdFx0aWYgb3B0aW9ucy5kaXJlY3Rpb24gPT0gXCJ2ZXJ0aWNhbFwiXG5cdFx0XHRcdGxheWVyLnkgPSBvZmZzZXRcblx0XHRcdFx0b2Zmc2V0ICs9IGxheWVyLmhlaWdodCArIG9wdGlvbnMubWFyZ2luXG5cdFx0XHRlbHNlXG5cdFx0XHRcdGxheWVyLnggPSBvZmZzZXRcblx0XHRcdFx0b2Zmc2V0ICs9IGxheWVyLndpZHRoICsgb3B0aW9ucy5tYXJnaW5cblxuXHRcdCMgUmVtZW1iZXIgd2hpY2ggbWV0aG9kIHdhcyB1c2VkXG5cdFx0dGhpcy5fc2V0TGF5ZXJNZXRhZGF0YShsYXllciwgJ21ldGhvZFVzZWQnLCAnc2FtZU1hcmdpbicpXG5cblx0IyBMYXllcnMgZmlsbCB1cCB0aGUgc3BhY2UgYmV0d2VlbiAwIGFuZCAnbWF4Jy4gVGhlIHNwYWNlXG5cdCMgYmV0d2VlbiB0aGUgbGF5ZXJzIGlzIGF1dG9tYXRpY2FsbHkgY2FsY3VsYXRlZC5cblx0c3BhY2VkOiAob3B0aW9ucykgLT5cblxuXHRcdCMgQXJndW1lbnRzIHRoYXQgYXJlIHVuaXF1ZSB0byB0aGlzIG1ldGhvZFxuXHRcdGRlZmF1bHRzID1cblx0XHRcdG1heDogMTAwMFxuXG5cdFx0IyBTZXQgdXAgb3B0aW9ucyBhbmQgdmFsaWRhdGUgcHJvcGVydGllc1xuXHRcdG9wdGlvbnMgPSBPYmplY3QuYXNzaWduKHt9LCB0aGlzLmdsb2JhbERlZmF1bHRzLCBkZWZhdWx0cywgb3B0aW9ucylcblx0XHR0aGlzLl92YWxpZGF0ZU9wdGlvbnMob3B0aW9ucylcblxuXHRcdCMgQ2FsY3VsYXRlIHRoZSBoZWlnaHQvd2lkdGggb2YgYWxsIGxheWVycyBjb21iaW5lZFxuXHRcdHRvdGFsQXJlYSA9IDBcblx0XHRmb3IgaW5kZXgsIGxheWVyIG9mIG9wdGlvbnMubGF5ZXJzXG5cdFx0XHRpZiBvcHRpb25zLmRpcmVjdGlvbiA9PSBcInZlcnRpY2FsXCJcblx0XHRcdFx0dG90YWxBcmVhICs9IGxheWVyLmhlaWdodFxuXHRcdFx0ZWxzZVxuXHRcdFx0XHR0b3RhbEFyZWEgKz0gbGF5ZXIud2lkdGhcblxuXHRcdCMgQ2FsY3VsYXRlIHRoZSBzcGFjaW5nIGJldHdlZW4gZWFjaCBsYXllclxuXHRcdHNwYWNpbmcgPSAob3B0aW9ucy5tYXggLSB0b3RhbEFyZWEpIC8gKG9wdGlvbnMubGF5ZXJzLmxlbmd0aCAtIDEpXG5cblx0XHQjIExvb3AgdGhyb3VnaCBhbGwgbGF5ZXJzIGFuZCBwb3NpdGlvbiB0aGVtXG5cdFx0b2Zmc2V0ID0gb3B0aW9ucy5zdGFydE9mZnNldFxuXHRcdGZvciBpbmRleCwgbGF5ZXIgb2Ygb3B0aW9ucy5sYXllcnNcblx0XHRcdGlmIG9wdGlvbnMuZGlyZWN0aW9uID09IFwidmVydGljYWxcIlxuXHRcdFx0XHRsYXllci55ID0gb2Zmc2V0XG5cdFx0XHRlbHNlXG5cdFx0XHRcdGxheWVyLnggPSBvZmZzZXRcblx0XHRcdG9mZnNldCArPSBsYXllci5oZWlnaHQgKyBzcGFjaW5nXG5cblx0XHQjIFJlbWVtYmVyIHdoaWNoIG1ldGhvZCB3YXMgdXNlZFxuXHRcdHRoaXMuX3NldExheWVyTWV0YWRhdGEobGF5ZXIsICdtZXRob2RVc2VkJywgJ3NwYWNlZCcpXG5cblx0IyBTaW1wbGUgdmFsaWRhdGlvbiBmb3Igb3B0aW9ucyBvYmplY3RzLiBEZXNpZ25lZCB0byBiZSBiZWdpbm5lci1mcmllbmRseS5cblx0X3ZhbGlkYXRlT3B0aW9uczogKG9wdGlvbnMpIC0+XG5cblx0XHRpZiAhb3B0aW9ucy5sYXllcnNcblx0XHRcdHRocm93IHRoaXMuX2Vycm9yKCdub0xheWVycycpXG5cblx0XHRpZiAhXy5pc0FycmF5KG9wdGlvbnMubGF5ZXJzKVxuXHRcdFx0dGhyb3cgdGhpcy5fZXJyb3IoJ2xheWVyc05vdEFycmF5JylcblxuXHRcdGlmIG9wdGlvbnMubGF5ZXJzLmxlbmd0aCA9PSAwXG5cdFx0XHR0aHJvdyB0aGlzLl9lcnJvcignbGF5ZXJzQXJyYXlFbXB0eScpXG5cblx0XHRpZiB0eXBlb2Ygb3B0aW9ucy5tYXJnaW4gPT0gXCJzdHJpbmdcIlxuXHRcdFx0dGhyb3cgdGhpcy5fZXJyb3IoJ251bWJlckFzU3RyaW5nJywgb3B0aW9ucy5tYXJnaW4pXG5cblx0XHRpZiB0eXBlb2Ygb3B0aW9ucy5zdGFydE9mZnNldCA9PSBcInN0cmluZ1wiXG5cdFx0XHR0aHJvdyB0aGlzLl9lcnJvcignbnVtYmVyQXNTdHJpbmcnLCBvcHRpb25zLnN0YXJ0T2Zmc2V0KVxuXG5cdCMgVGhyb3dzIGRpZmZlcmVudCBlcnJvcnMgZm9yIGRpZmZlcmVudCBlcnJvciBjb2Rlc1xuXHRfZXJyb3I6IChpZCwgdmFsdWUpIC0+XG5cdFx0ZXJyID0gbnVsbFxuXHRcdGlmIGlkID09IFwibnVtYmVyQXNTdHJpbmdcIlxuXHRcdFx0ZXJyID0gbmV3IEVycm9yIFwiRG9uJ3QgcHV0IHF1b3RhdGlvbiBtYXJrcyBhcm91bmQgbnVtYmVycy4gXCIgKyBcIlxcXCJcIiArIHZhbHVlICsgXCJcXFwiIHNob3VsZCBiZSB3cml0dGVuIGFzIFwiICsgdmFsdWUgKyBcIi5cIlxuXHRcdGlmIGlkID09IFwibm9MYXllcnNcIlxuXHRcdFx0ZXJyID0gbmV3IEVycm9yIFwiWW91IGRpZG4ndCBnaXZlIGRpc3RyaWJ1dGVMYXllcnMubGF5ZXJzIGFueSB2YWx1ZVwiXG5cdFx0aWYgaWQgPT0gXCJsYXllcnNOb3RBcnJheVwiXG5cdFx0XHRlcnIgPSBuZXcgRXJyb3IgXCJkaXN0cmlidXRlTGF5ZXJzLmxheWVycyBleHBlY3RzIGFuIGFycmF5XCJcblx0XHRpZiBpZCA9PSBcImxheWVyc0FycmF5RW1wdHlcIlxuXHRcdFx0ZXJyID0gbmV3IEVycm9yIFwiVGhlIGFycmF5IHRoYXQgeW91IHBhc3NlZCB0byBkaXN0cmlidXRlTGF5ZXJzLmxheWVycyB3YXMgZW1wdHlcIlxuXHRcdHJldHVybiBlcnJcblxuXHQjIEF0dGFjaGVzIGN1c3RvbSBtZXRhZGF0YSB0byBsYXllcnNcblx0X3NldExheWVyTWV0YWRhdGE6IChsYXllciwga2V5LCB2YWx1ZSkgLT5cblx0XHRpZiAhbGF5ZXIuY3VzdG9tIHRoZW4gbGF5ZXIuY3VzdG9tID0ge31cblx0XHRsYXllci5jdXN0b20uZGlzdHJpYnV0ZUxheWVycyA9IHt9XG5cdFx0bGF5ZXIuY3VzdG9tLmRpc3RyaWJ1dGVMYXllcnNba2V5XSA9IHZhbHVlXG4iLCJcblxuXG4jICdGaXJlYmFzZSBSRVNUIEFQSSBDbGFzcycgbW9kdWxlIHYxLjBcbiMgYnkgTWFyYyBLcmVubiwgTWF5IDMxc3QsIDIwMTYgfCBtYXJjLmtyZW5uQGdtYWlsLmNvbSB8IEBtYXJjX2tyZW5uXG5cbiMgRG9jdW1lbnRhdGlvbiBvZiB0aGlzIE1vZHVsZTogaHR0cHM6Ly9naXRodWIuY29tL21hcmNrcmVubi9mcmFtZXItRmlyZWJhc2VcbiMgLS0tLS0tIDogLS0tLS0tLSBGaXJlYmFzZSBSRVNUIEFQSTogaHR0cHM6Ly9maXJlYmFzZS5nb29nbGUuY29tL2RvY3MvcmVmZXJlbmNlL3Jlc3QvZGF0YWJhc2UvXG5cblxuIyBUb0RvOlxuIyBGaXggb25DaGFuZ2UgXCJjb25uZWN0aW9uXCIsIGB0aGlzwrQgY29udGV4dFxuXG5cblxuIyBGaXJlYmFzZSBSRVNUIEFQSSBDbGFzcyAtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG5cbmNsYXNzIGV4cG9ydHMuRmlyZWJhc2UgZXh0ZW5kcyBGcmFtZXIuQmFzZUNsYXNzXG5cblxuXG5cdGdldENPUlN1cmwgPSAoc2VydmVyLCBwYXRoLCBzZWNyZXQsIHByb2plY3QpIC0+XG5cblx0XHRzd2l0Y2ggVXRpbHMuaXNXZWJLaXQoKVxuXHRcdFx0d2hlbiB0cnVlIHRoZW4gdXJsID0gXCJodHRwczovLyN7c2VydmVyfSN7cGF0aH0uanNvbj9hdXRoPSN7c2VjcmV0fSZucz0je3Byb2plY3R9JnNzZT10cnVlXCIgIyBXZWJraXQgWFNTIHdvcmthcm91bmRcblx0XHRcdGVsc2UgICAgICAgICAgIHVybCA9IFwiaHR0cHM6Ly8je3Byb2plY3R9LmZpcmViYXNlaW8uY29tI3twYXRofS5qc29uP2F1dGg9I3tzZWNyZXR9XCJcblxuXHRcdHJldHVybiB1cmxcblxuXG5cdEAuZGVmaW5lIFwic3RhdHVzXCIsXG5cdFx0Z2V0OiAtPiBAX3N0YXR1cyAjIHJlYWRPbmx5XG5cblx0Y29uc3RydWN0b3I6IChAb3B0aW9ucz17fSkgLT5cblx0XHRAcHJvamVjdElEID0gQG9wdGlvbnMucHJvamVjdElEID89IG51bGxcblx0XHRAc2VjcmV0ICAgID0gQG9wdGlvbnMuc2VjcmV0ICAgID89IG51bGxcblx0XHRAc2VydmVyICAgID0gQG9wdGlvbnMuc2VydmVyICAgID89IHVuZGVmaW5lZCAjIHJlcXVpcmVkIGZvciBXZWJLaXQgWFNTIHdvcmthcm91bmRcblx0XHRAZGVidWcgICAgID0gQG9wdGlvbnMuZGVidWcgICAgID89IGZhbHNlXG5cdFx0QF9zdGF0dXMgICAgICAgICAgICAgICAgICAgICAgICA/PSBcImRpc2Nvbm5lY3RlZFwiXG5cdFx0c3VwZXJcblxuXG5cdFx0aWYgQHNlcnZlciBpcyB1bmRlZmluZWRcblx0XHRcdFV0aWxzLmRvbUxvYWRKU09OIFwiaHR0cHM6Ly8je0Bwcm9qZWN0SUR9LmZpcmViYXNlaW8uY29tLy5zZXR0aW5ncy9vd25lci5qc29uXCIsIChhLHNlcnZlcikgLT5cblx0XHRcdFx0cHJpbnQgbXNnID0gXCJBZGQgX19fX19fIHNlcnZlcjpcIiArICcgICBcIicgKyBzZXJ2ZXIgKyAnXCInICsgXCIgX19fX18gdG8geW91ciBpbnN0YW5jZSBvZiBGaXJlYmFzZS5cIlxuXHRcdFx0XHRjb25zb2xlLmxvZyBcIkZpcmViYXNlOiAje21zZ31cIiBpZiBAZGVidWdcblxuXG5cdFx0Y29uc29sZS5sb2cgXCJGaXJlYmFzZTogQ29ubmVjdGluZyB0byBGaXJlYmFzZSBQcm9qZWN0ICcje0Bwcm9qZWN0SUR9JyAuLi4gXFxuIFVSTDogJyN7Z2V0Q09SU3VybChAc2VydmVyLCBcIi9cIiwgQHNlY3JldCwgQHByb2plY3RJRCl9J1wiIGlmIEBkZWJ1Z1xuXHRcdEAub25DaGFuZ2UgXCJjb25uZWN0aW9uXCJcblxuXG5cdHJlcXVlc3QgPSAocHJvamVjdCwgc2VjcmV0LCBwYXRoLCBjYWxsYmFjaywgbWV0aG9kLCBkYXRhLCBwYXJhbWV0ZXJzLCBkZWJ1ZykgLT5cblxuXHRcdHVybCA9IFwiaHR0cHM6Ly8je3Byb2plY3R9LmZpcmViYXNlaW8uY29tI3twYXRofS5qc29uP2F1dGg9I3tzZWNyZXR9XCJcblxuXG5cdFx0dW5sZXNzIHBhcmFtZXRlcnMgaXMgdW5kZWZpbmVkXG5cdFx0XHRpZiBwYXJhbWV0ZXJzLnNoYWxsb3cgICAgICAgICAgICB0aGVuIHVybCArPSBcIiZzaGFsbG93PXRydWVcIlxuXHRcdFx0aWYgcGFyYW1ldGVycy5mb3JtYXQgaXMgXCJleHBvcnRcIiB0aGVuIHVybCArPSBcIiZmb3JtYXQ9ZXhwb3J0XCJcblxuXHRcdFx0c3dpdGNoIHBhcmFtZXRlcnMucHJpbnRcblx0XHRcdFx0d2hlbiBcInByZXR0eVwiIHRoZW4gdXJsICs9IFwiJnByaW50PXByZXR0eVwiXG5cdFx0XHRcdHdoZW4gXCJzaWxlbnRcIiB0aGVuIHVybCArPSBcIiZwcmludD1zaWxlbnRcIlxuXG5cdFx0XHRpZiB0eXBlb2YgcGFyYW1ldGVycy5kb3dubG9hZCBpcyBcInN0cmluZ1wiXG5cdFx0XHRcdHVybCArPSBcIiZkb3dubG9hZD0je3BhcmFtZXRlcnMuZG93bmxvYWR9XCJcblx0XHRcdFx0d2luZG93Lm9wZW4odXJsLFwiX3NlbGZcIilcblxuXG5cdFx0XHR1cmwgKz0gXCImb3JkZXJCeT1cIiArICdcIicgKyBwYXJhbWV0ZXJzLm9yZGVyQnkgKyAnXCInIGlmIHR5cGVvZiBwYXJhbWV0ZXJzLm9yZGVyQnkgICAgICBpcyBcInN0cmluZ1wiXG5cdFx0XHR1cmwgKz0gXCImbGltaXRUb0ZpcnN0PSN7cGFyYW1ldGVycy5saW1pdFRvRmlyc3R9XCIgICBpZiB0eXBlb2YgcGFyYW1ldGVycy5saW1pdFRvRmlyc3QgaXMgXCJudW1iZXJcIlxuXHRcdFx0dXJsICs9IFwiJmxpbWl0VG9MYXN0PSN7cGFyYW1ldGVycy5saW1pdFRvTGFzdH1cIiAgICAgaWYgdHlwZW9mIHBhcmFtZXRlcnMubGltaXRUb0xhc3QgIGlzIFwibnVtYmVyXCJcblx0XHRcdHVybCArPSBcIiZzdGFydEF0PSN7cGFyYW1ldGVycy5zdGFydEF0fVwiICAgICAgICAgICAgIGlmIHR5cGVvZiBwYXJhbWV0ZXJzLnN0YXJ0QXQgICAgICBpcyBcIm51bWJlclwiXG5cdFx0XHR1cmwgKz0gXCImZW5kQXQ9I3twYXJhbWV0ZXJzLmVuZEF0fVwiICAgICAgICAgICAgICAgICBpZiB0eXBlb2YgcGFyYW1ldGVycy5lbmRBdCAgICAgICAgaXMgXCJudW1iZXJcIlxuXHRcdFx0dXJsICs9IFwiJmVxdWFsVG89I3twYXJhbWV0ZXJzLmVxdWFsVG99XCIgICAgICAgICAgICAgaWYgdHlwZW9mIHBhcmFtZXRlcnMuZXF1YWxUbyAgICAgIGlzIFwibnVtYmVyXCJcblxuXG5cdFx0eGh0dHAgPSBuZXcgWE1MSHR0cFJlcXVlc3Rcblx0XHRjb25zb2xlLmxvZyBcIkZpcmViYXNlOiBOZXcgJyN7bWV0aG9kfSctcmVxdWVzdCB3aXRoIGRhdGE6ICcje0pTT04uc3RyaW5naWZ5KGRhdGEpfScgXFxuIFVSTDogJyN7dXJsfSdcIiBpZiBkZWJ1Z1xuXHRcdHhodHRwLm9ucmVhZHlzdGF0ZWNoYW5nZSA9ID0+XG5cblx0XHRcdHVubGVzcyBwYXJhbWV0ZXJzIGlzIHVuZGVmaW5lZFxuXHRcdFx0XHRpZiBwYXJhbWV0ZXJzLnByaW50IGlzIFwic2lsZW50XCIgb3IgdHlwZW9mIHBhcmFtZXRlcnMuZG93bmxvYWQgaXMgXCJzdHJpbmdcIiB0aGVuIHJldHVybiAjIHVnaFxuXG5cdFx0XHRzd2l0Y2ggeGh0dHAucmVhZHlTdGF0ZVxuXHRcdFx0XHR3aGVuIDAgdGhlbiBjb25zb2xlLmxvZyBcIkZpcmViYXNlOiBSZXF1ZXN0IG5vdCBpbml0aWFsaXplZCBcXG4gVVJMOiAnI3t1cmx9J1wiICAgICAgIGlmIGRlYnVnXG5cdFx0XHRcdHdoZW4gMSB0aGVuIGNvbnNvbGUubG9nIFwiRmlyZWJhc2U6IFNlcnZlciBjb25uZWN0aW9uIGVzdGFibGlzaGVkIFxcbiBVUkw6ICcje3VybH0nXCIgaWYgZGVidWdcblx0XHRcdFx0d2hlbiAyIHRoZW4gY29uc29sZS5sb2cgXCJGaXJlYmFzZTogUmVxdWVzdCByZWNlaXZlZCBcXG4gVVJMOiAnI3t1cmx9J1wiICAgICAgICAgICAgICBpZiBkZWJ1Z1xuXHRcdFx0XHR3aGVuIDMgdGhlbiBjb25zb2xlLmxvZyBcIkZpcmViYXNlOiBQcm9jZXNzaW5nIHJlcXVlc3QgXFxuIFVSTDogJyN7dXJsfSdcIiAgICAgICAgICAgIGlmIGRlYnVnXG5cdFx0XHRcdHdoZW4gNFxuXHRcdFx0XHRcdGNhbGxiYWNrKEpTT04ucGFyc2UoeGh0dHAucmVzcG9uc2VUZXh0KSkgaWYgY2FsbGJhY2s/XG5cdFx0XHRcdFx0Y29uc29sZS5sb2cgXCJGaXJlYmFzZTogUmVxdWVzdCBmaW5pc2hlZCwgcmVzcG9uc2U6ICcje0pTT04ucGFyc2UoeGh0dHAucmVzcG9uc2VUZXh0KX0nIFxcbiBVUkw6ICcje3VybH0nXCIgaWYgZGVidWdcblxuXHRcdFx0aWYgeGh0dHAuc3RhdHVzIGlzIFwiNDA0XCJcblx0XHRcdFx0Y29uc29sZS53YXJuIFwiRmlyZWJhc2U6IEludmFsaWQgcmVxdWVzdCwgcGFnZSBub3QgZm91bmQgXFxuIFVSTDogJyN7dXJsfSdcIiBpZiBkZWJ1Z1xuXG5cblx0XHR4aHR0cC5vcGVuKG1ldGhvZCwgdXJsLCB0cnVlKVxuXHRcdHhodHRwLnNldFJlcXVlc3RIZWFkZXIoXCJDb250ZW50LXR5cGVcIiwgXCJhcHBsaWNhdGlvbi9qc29uOyBjaGFyc2V0PXV0Zi04XCIpXG5cdFx0eGh0dHAuc2VuZChkYXRhID0gXCIje0pTT04uc3RyaW5naWZ5KGRhdGEpfVwiKVxuXG5cblxuXHQjIEF2YWlsYWJsZSBtZXRob2RzXG5cblx0Z2V0OiAgICAocGF0aCwgY2FsbGJhY2ssICAgICAgIHBhcmFtZXRlcnMpIC0+IHJlcXVlc3QoQHByb2plY3RJRCwgQHNlY3JldCwgcGF0aCwgY2FsbGJhY2ssIFwiR0VUXCIsICAgIG51bGwsIHBhcmFtZXRlcnMsIEBkZWJ1Zylcblx0cHV0OiAgICAocGF0aCwgZGF0YSwgY2FsbGJhY2ssIHBhcmFtZXRlcnMpIC0+IHJlcXVlc3QoQHByb2plY3RJRCwgQHNlY3JldCwgcGF0aCwgY2FsbGJhY2ssIFwiUFVUXCIsICAgIGRhdGEsIHBhcmFtZXRlcnMsIEBkZWJ1Zylcblx0cG9zdDogICAocGF0aCwgZGF0YSwgY2FsbGJhY2ssIHBhcmFtZXRlcnMpIC0+IHJlcXVlc3QoQHByb2plY3RJRCwgQHNlY3JldCwgcGF0aCwgY2FsbGJhY2ssIFwiUE9TVFwiLCAgIGRhdGEsIHBhcmFtZXRlcnMsIEBkZWJ1Zylcblx0cGF0Y2g6ICAocGF0aCwgZGF0YSwgY2FsbGJhY2ssIHBhcmFtZXRlcnMpIC0+IHJlcXVlc3QoQHByb2plY3RJRCwgQHNlY3JldCwgcGF0aCwgY2FsbGJhY2ssIFwiUEFUQ0hcIiwgIGRhdGEsIHBhcmFtZXRlcnMsIEBkZWJ1Zylcblx0ZGVsZXRlOiAocGF0aCwgY2FsbGJhY2ssICAgICAgIHBhcmFtZXRlcnMpIC0+IHJlcXVlc3QoQHByb2plY3RJRCwgQHNlY3JldCwgcGF0aCwgY2FsbGJhY2ssIFwiREVMRVRFXCIsIG51bGwsIHBhcmFtZXRlcnMsIEBkZWJ1ZylcblxuXG5cblx0b25DaGFuZ2U6IChwYXRoLCBjYWxsYmFjaykgLT5cblxuXG5cdFx0aWYgcGF0aCBpcyBcImNvbm5lY3Rpb25cIlxuXG5cdFx0XHR1cmwgPSBnZXRDT1JTdXJsKEBzZXJ2ZXIsIFwiL1wiLCBAc2VjcmV0LCBAcHJvamVjdElEKVxuXHRcdFx0Y3VycmVudFN0YXR1cyA9IFwiZGlzY29ubmVjdGVkXCJcblx0XHRcdHNvdXJjZSA9IG5ldyBFdmVudFNvdXJjZSh1cmwpXG5cblx0XHRcdHNvdXJjZS5hZGRFdmVudExpc3RlbmVyIFwib3BlblwiLCA9PlxuXHRcdFx0XHRpZiBjdXJyZW50U3RhdHVzIGlzIFwiZGlzY29ubmVjdGVkXCJcblx0XHRcdFx0XHRALl9zdGF0dXMgPSBcImNvbm5lY3RlZFwiXG5cdFx0XHRcdFx0Y2FsbGJhY2soXCJjb25uZWN0ZWRcIikgaWYgY2FsbGJhY2s/XG5cdFx0XHRcdFx0Y29uc29sZS5sb2cgXCJGaXJlYmFzZTogQ29ubmVjdGlvbiB0byBGaXJlYmFzZSBQcm9qZWN0ICcje0Bwcm9qZWN0SUR9JyBlc3RhYmxpc2hlZFwiIGlmIEBkZWJ1Z1xuXHRcdFx0XHRjdXJyZW50U3RhdHVzID0gXCJjb25uZWN0ZWRcIlxuXG5cdFx0XHRzb3VyY2UuYWRkRXZlbnRMaXN0ZW5lciBcImVycm9yXCIsID0+XG5cdFx0XHRcdGlmIGN1cnJlbnRTdGF0dXMgaXMgXCJjb25uZWN0ZWRcIlxuXHRcdFx0XHRcdEAuX3N0YXR1cyA9IFwiZGlzY29ubmVjdGVkXCJcblx0XHRcdFx0XHRjYWxsYmFjayhcImRpc2Nvbm5lY3RlZFwiKSBpZiBjYWxsYmFjaz9cblx0XHRcdFx0XHRjb25zb2xlLndhcm4gXCJGaXJlYmFzZTogQ29ubmVjdGlvbiB0byBGaXJlYmFzZSBQcm9qZWN0ICcje0Bwcm9qZWN0SUR9JyBjbG9zZWRcIiBpZiBAZGVidWdcblx0XHRcdFx0Y3VycmVudFN0YXR1cyA9IFwiZGlzY29ubmVjdGVkXCJcblxuXG5cdFx0ZWxzZVxuXG5cdFx0XHR1cmwgPSBnZXRDT1JTdXJsKEBzZXJ2ZXIsIHBhdGgsIEBzZWNyZXQsIEBwcm9qZWN0SUQpXG5cdFx0XHRzb3VyY2UgPSBuZXcgRXZlbnRTb3VyY2UodXJsKVxuXHRcdFx0Y29uc29sZS5sb2cgXCJGaXJlYmFzZTogTGlzdGVuaW5nIHRvIGNoYW5nZXMgbWFkZSB0byAnI3twYXRofScgXFxuIFVSTDogJyN7dXJsfSdcIiBpZiBAZGVidWdcblxuXHRcdFx0c291cmNlLmFkZEV2ZW50TGlzdGVuZXIgXCJwdXRcIiwgKGV2KSA9PlxuXHRcdFx0XHRjYWxsYmFjayhKU09OLnBhcnNlKGV2LmRhdGEpLmRhdGEsIFwicHV0XCIsIEpTT04ucGFyc2UoZXYuZGF0YSkucGF0aCwgXy5yZXN0KEpTT04ucGFyc2UoZXYuZGF0YSkucGF0aC5zcGxpdChcIi9cIiksMSkpIGlmIGNhbGxiYWNrP1xuXHRcdFx0XHRjb25zb2xlLmxvZyBcIkZpcmViYXNlOiBSZWNlaXZlZCBjaGFuZ2VzIG1hZGUgdG8gJyN7cGF0aH0nIHZpYSAnUFVUJzogI3tKU09OLnBhcnNlKGV2LmRhdGEpLmRhdGF9IFxcbiBVUkw6ICcje3VybH0nXCIgaWYgQGRlYnVnXG5cblx0XHRcdHNvdXJjZS5hZGRFdmVudExpc3RlbmVyIFwicGF0Y2hcIiwgKGV2KSA9PlxuXHRcdFx0XHRjYWxsYmFjayhKU09OLnBhcnNlKGV2LmRhdGEpLmRhdGEsIFwicGF0Y2hcIiwgSlNPTi5wYXJzZShldi5kYXRhKS5wYXRoLCBfLnJlc3QoSlNPTi5wYXJzZShldi5kYXRhKS5wYXRoLnNwbGl0KFwiL1wiKSwxKSkgaWYgY2FsbGJhY2s/XG5cdFx0XHRcdGNvbnNvbGUubG9nIFwiRmlyZWJhc2U6IFJlY2VpdmVkIGNoYW5nZXMgbWFkZSB0byAnI3twYXRofScgdmlhICdQQVRDSCc6ICN7SlNPTi5wYXJzZShldi5kYXRhKS5kYXRhfSBcXG4gVVJMOiAnI3t1cmx9J1wiIGlmIEBkZWJ1Z1xuXG4iLCJtYWtlU3RyID0gKG9iaikgLT5cbiAgICBncmFkU3RyaW5nID0gb2JqLnR5cGUgKyBcIi1ncmFkaWVudChcIlxuXG4gICAgaWYgb2JqLnR5cGUgPT0gXCJyYWRpYWxcIiAmJiBvYmouc2hhcGVcbiAgICAgICAgZ3JhZFN0cmluZyArPSBvYmouc2hhcGUgKyBcIiwgXCIgIFxuICAgICAgICBcbiAgICBpZiBvYmoudHlwZSA9PSBcImxpbmVhclwiICYmIG9iai5hbmdsZVxuICAgICAgICBncmFkU3RyaW5nICs9IG9iai5hbmdsZSArIFwiLCBcIlxuXG4gICAgZm9yIGkgaW4gWzAuLm9iai5jb2xvcnMubGVuZ3RoLTFdIGJ5IDFcbiAgICAgICAgaWYgaSA9PSBvYmouY29sb3JzLmxlbmd0aC0xXG4gICAgICAgICAgICBncmFkU3RyaW5nICs9IG9iai5jb2xvcnNbaV0gKyBcIlwiXG4gICAgICAgIGVsc2VcbiAgICAgICAgICAgIGdyYWRTdHJpbmcgKz0gb2JqLmNvbG9yc1tpXSArIFwiLCBcIlxuXG4gICAgZ3JhZFN0cmluZyArPSBcIilcIlxuICAgIFxuICAgIHJldHVybiBncmFkU3RyaW5nXG5cblxuZXhwb3J0cy5yYWRpYWwgPSAoIGxheWVyLCBjb2xvckFyciwgc2hhcGUgKSAtPlxuICAgIG9iaiA9IHtcbiAgICAgICAgc2hhcGU6IHNoYXBlLFxuICAgICAgICBjb2xvcnM6IGNvbG9yQXJyLFxuICAgICAgICB0eXBlOiBcInJhZGlhbFwiXG4gICAgfVxuXG4gICAgbGF5ZXIuc3R5bGVbXCJiYWNrZ3JvdW5kLWltYWdlXCJdID0gbWFrZVN0cihvYmopXG5cbmV4cG9ydHMubGluZWFyID0gKCBsYXllciwgY29sb3JBcnIsIGFuZ2xlICkgLT5cbiAgICBvYmogPSB7XG4gICAgICAgIGFuZ2xlOiBhbmdsZSxcbiAgICAgICAgY29sb3JzOiBjb2xvckFycixcbiAgICAgICAgdHlwZTogXCJsaW5lYXJcIlxuICAgIH1cblxuICAgIGxheWVyLnN0eWxlW1wiYmFja2dyb3VuZC1pbWFnZVwiXSA9IG1ha2VTdHIob2JqKSJdfQ==
