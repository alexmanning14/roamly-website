// Roamly trip map for the web: a MapKit JS port of the app's
// ItineraryRouteMapView + ItineraryMapModel (Roamly/Views, Roamly/ViewModels).
// Same rules as the app: day pins and route legs from each day's city, place
// pins only for the focused day, stop numbers from the day's timeline order,
// coral halo + dashed core route lines, and the fitFocusedDay framing maths.
(function (global) {
  "use strict";

  // GeoColors (Roamly/Extensions.swift)
  var C = { teal: "#4FC4B0", coral: "#E7A684", clayRose: "#CC7F6E" };
  var CORAL_85 = "rgba(231,166,132,0.85)";

  // RoutePlaceAnnotation.tint
  function placeTint(type) {
    if (type === "food") return C.coral;
    if (type === "housing") return C.clayRose;
    return C.teal; // activity, place, flight, note
  }

  // ItineraryDay.timelineBlocks / stopNumbers
  function timelineBlocks(day) {
    return day.blocks.filter(function (b) { return b.type !== "flight" && b.type !== "housing"; })
      .slice().sort(function (a, b) { return a.startHour - b.startHour; });
  }
  function stopNumbers(day) {
    var n = {};
    timelineBlocks(day).forEach(function (b, i) { if (n[b.id] == null) n[b.id] = i + 1; });
    return n;
  }

  // ItineraryMapModel.resolvePin (city coordinate per day)
  function dayPins(days) {
    return days.map(function (d, i) {
      return d.latitude == null ? null : { id: i, lat: d.latitude, lon: d.longitude, city: d.city, country: d.country };
    }).filter(Boolean);
  }

  // MapGlobeRepresentable: curvedRoutePoints, routeEdgeKey, travel time helpers
  function curvedRoutePoints(stops, curveFactor, samples) {
    curveFactor = curveFactor || 0.13; samples = samples || 22;
    var out = [];
    for (var i = 0; i < stops.length - 1; i++) {
      var a = stops[i], b = stops[i + 1];
      var k = Math.max(0.1, Math.cos(((a.lat + b.lat) / 2) * Math.PI / 180));
      var ax = a.lon * k, ay = a.lat, bx = b.lon * k, by = b.lat;
      var dx = bx - ax, dy = by - ay, len = Math.sqrt(dx * dx + dy * dy);
      if (!len) continue;
      var off = len * curveFactor;
      var cx = (ax + bx) / 2 + (-dy / len) * off, cy = (ay + by) / 2 + (dx / len) * off;
      for (var s = (i === 0 ? 0 : 1); s <= samples; s++) {
        var t = s / samples, o = 1 - t;
        out.push({ lat: o * o * ay + 2 * o * t * cy + t * t * by, lon: (o * o * ax + 2 * o * t * cx + t * t * bx) / k });
      }
    }
    return out;
  }
  function edgeKey(a, b) {
    var p = [a.lat, a.lon], q = [b.lat, b.lon];
    var lo = (p[0] < q[0] || (p[0] === q[0] && p[1] <= q[1])) ? p : q, hi = lo === p ? q : p;
    return lo.join(",") + "|" + hi.join(",");
  }
  function distance(a, b) {
    var R = 6371000, r = Math.PI / 180;
    var dLat = (b.lat - a.lat) * r, dLon = (b.lon - a.lon) * r;
    var h = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return 2 * R * Math.asin(Math.sqrt(h));
  }
  function formatTravelTime(sec, approximate) {
    var total = Math.max(1, Math.round(sec / 60)), h = Math.floor(total / 60), m = total % 60;
    var core = h > 0 && m > 0 ? h + "h " + m + "m" : h > 0 ? h + "h" : m + "m";
    return approximate ? "~" + core : core;
  }
  function midpoint(coords) {
    if (coords.length <= 2) {
      var f = coords[0], l = coords[coords.length - 1];
      return { lat: (f.lat + l.lat) / 2, lon: (f.lon + l.lon) / 2 };
    }
    var cum = [0], total = 0;
    for (var i = 1; i < coords.length; i++) { total += distance(coords[i - 1], coords[i]); cum.push(total); }
    var half = total / 2;
    for (var j = 1; j < coords.length; j++) if (cum[j] >= half) {
      var seg = cum[j] - cum[j - 1], t = seg > 0 ? (half - cum[j - 1]) / seg : 0, a = coords[j - 1], b = coords[j];
      return { lat: a.lat + (b.lat - a.lat) * t, lon: a.lon + (b.lon - a.lon) * t };
    }
    return coords[Math.floor(coords.length / 2)];
  }

  var legCache = {};
  // resolveRouteLeg: >=700 km flies; otherwise Apple directions, with the same fallbacks.
  function resolveRouteLeg(a, b) {
    var key = edgeKey(a, b);
    if (legCache[key]) return Promise.resolve(legCache[key]);
    var dist = distance(a, b), arc = curvedRoutePoints([a, b]);
    function leg(coords, mode, time, approx) {
      return { coords: coords, mode: mode, time: time == null ? null : formatTravelTime(time, approx), mid: midpoint(coords) };
    }
    var flight = function () { return leg(arc, "flying", dist / 222 + 3600, true); };
    if (dist >= 700000) return Promise.resolve(legCache[key] = flight());
    return new Promise(function (resolve) {
      new mapkit.Directions().route({
        origin: new mapkit.Coordinate(a.lat, a.lon), destination: new mapkit.Coordinate(b.lat, b.lon),
        transportType: mapkit.Directions.Transport.Automobile, requestsAlternateRoutes: false
      }, function (err, data) {
        var r = !err && data && data.routes && data.routes.slice().sort(function (x, y) { return x.expectedTravelTime - y.expectedTravelTime; })[0];
        var out;
        if (r && r.expectedTravelTime <= 8 * 3600) {
          var pts = (r.polyline.points || []).map(function (c) { return { lat: c.latitude, lon: c.longitude }; });
          out = leg(pts.length ? pts : arc, "driving", r.expectedTravelTime, false);
        } else if (r) out = flight();
        else out = leg(arc, "driving", (dist * 1.25) / 15.3, true);
        resolve(legCache[key] = out);
      });
    });
  }

  function coord(p) { return new mapkit.Coordinate(p.lat, p.lon); }
  function line(points, width, alpha, dashed) {
    return new mapkit.PolylineOverlay(points.map(coord), {
      style: new mapkit.Style({ strokeColor: C.coral, strokeOpacity: alpha, lineWidth: width, lineCap: "round", lineJoin: "round", lineDash: dashed ? [3, 7] : [] }),
      enabled: false
    });
  }
  // makeRouteLabelView: coral pill with a car or plane glyph and the leg time.
  var CAR = '<svg viewBox="0 0 24 24" width="13" height="13" fill="#fff"><path d="M5 11l1.5-4.5A2 2 0 0 1 8.4 5h7.2a2 2 0 0 1 1.9 1.5L19 11a2 2 0 0 1 2 2v4a1 1 0 0 1-1 1h-1a2 2 0 0 1-4 0H9a2 2 0 0 1-4 0H4a1 1 0 0 1-1-1v-4a2 2 0 0 1 2-2zm2.1 0h9.8l-1-3.2a1 1 0 0 0-1-.8H9.1a1 1 0 0 0-1 .8z"/></svg>';
  var PLANE = '<svg viewBox="0 0 24 24" width="13" height="13" fill="#fff"><path d="M21 15.5v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V8.5l-8 5v2l8-2.5V18l-2 1.5V21l3.5-1 3.5 1v-1.5L13 18v-5z"/></svg>';
  function routeLabel(leg) {
    return new mapkit.Annotation(coord(leg.mid), function () {
      var el = document.createElement("div");
      el.className = "rm-leg";
      el.innerHTML = (leg.mode === "driving" ? CAR : PLANE) + (leg.time ? "<span>" + leg.time + "</span>" : "");
      return el;
    }, { displayPriority: 1000, enabled: false, anchorOffset: new DOMPoint(0, 0) });
  }

  function TripMap(el, trip, opts) {
    opts = opts || {};
    var self = this;
    this.trip = trip;
    this.onSelectBlock = opts.onSelectBlock || function () {};
    this.padding = opts.padding || { top: 70, right: 50, bottom: 50, left: 50 };
    var dark = opts.dark;
    var map = this.map = new mapkit.Map(el, {
      mapType: mapkit.Map.MapTypes.MutedStandard,       // MKStandardMapConfiguration(emphasisStyle: .muted)
      pointOfInterestFilter: mapkit.PointOfInterestFilter.excludingAllCategories,
      colorScheme: dark ? mapkit.Map.ColorSchemes.Dark : mapkit.Map.ColorSchemes.Light,
      showsCompass: mapkit.FeatureVisibility.Hidden, showsScale: mapkit.FeatureVisibility.Hidden,
      showsMapTypeControl: false, showsZoomControl: true, isRotationEnabled: false,
      showsPointsOfInterest: false
    });
    map.padding = new mapkit.Padding(this.padding.top, this.padding.right, this.padding.bottom, this.padding.left);
    this.route = dayPins(trip.days);
    this.focused = -1;
    this.cityAnns = []; this.placeAnns = []; this.byBlock = {};
    this.lastGlide = null;
    this.silent = false;
    map.addEventListener("select", function (e) {
      var a = e.annotation;
      if (self.silent || !a || !a.blockId) return;
      setTimeout(function () { a.selected = false; }, 0);
      self.onSelectBlock(a.blockId);
    });
    this.buildRoute();
  }

  // rebuildRouteOverlays
  TripMap.prototype.buildRoute = function () {
    var map = this.map, coords = [];
    this.route.forEach(function (p) {
      var last = coords[coords.length - 1];
      if (last && Math.abs(last.lat - p.lat) < 0.0001 && Math.abs(last.lon - p.lon) < 0.0001) return;
      coords.push(p);
    });
    if (coords.length < 2) return;
    var seen = {}, legs = [];
    for (var i = 0; i < coords.length - 1; i++) {
      var k = edgeKey(coords[i], coords[i + 1]);
      if (seen[k]) continue; seen[k] = 1; legs.push([coords[i], coords[i + 1]]);
    }
    var placeholders = {};
    legs.forEach(function (l) {
      var ph = line(curvedRoutePoints(l), 2.5, 0.35, true);
      placeholders[edgeKey(l[0], l[1])] = ph; map.addOverlay(ph);
    });
    legs.reduce(function (p, l) {
      return p.then(function () {
        return resolveRouteLeg(l[0], l[1]).then(function (leg) {
          var ph = placeholders[edgeKey(l[0], l[1])]; if (ph) map.removeOverlay(ph);
          if (leg.coords.length < 2) return;
          map.addOverlays([line(leg.coords, 5, 0.22, false), line(leg.coords, 2.5, 1, true)]);
          map.addAnnotation(routeLabel(leg));
        });
      });
    }, Promise.resolve());
  };

  // rebuildCityAnnotations
  TripMap.prototype.buildCities = function () {
    var map = this.map, focused = this.focused;
    if (this.cityAnns.length) map.removeAnnotations(this.cityAnns);
    this.cityAnns = this.route.map(function (p) {
      var on = p.id === focused;
      return new mapkit.MarkerAnnotation(coord(p), {
        title: p.city || p.country, glyphText: String(p.id + 1),
        color: on ? C.teal : CORAL_85, glyphColor: "#fff",
        titleVisibility: mapkit.FeatureVisibility.Adaptive,
        displayPriority: on ? mapkit.Annotation.DisplayPriority.Required : mapkit.Annotation.DisplayPriority.High,
        calloutEnabled: false, enabled: false
      });
    });
    map.addAnnotations(this.cityAnns);
  };

  // rebuildFocusedPlaces + rebuildPlaceAnnotations
  TripMap.prototype.buildPlaces = function () {
    var map = this.map, self = this;
    if (this.placeAnns.length) map.removeAnnotations(this.placeAnns);
    this.placeAnns = []; this.byBlock = {};
    var day = this.trip.days[this.focused]; if (!day) return;
    var nums = stopNumbers(day);
    day.blocks.forEach(function (b) {
      if (!b.mapPlace) return;
      var n = nums[b.id];
      var a = new mapkit.MarkerAnnotation(new mapkit.Coordinate(b.mapPlace.latitude, b.mapPlace.longitude), {
        title: b.title || b.mapPlace.name, color: placeTint(b.type), glyphColor: "#fff",
        glyphText: n != null ? String(n) : "", titleVisibility: mapkit.FeatureVisibility.Adaptive,
        displayPriority: mapkit.Annotation.DisplayPriority.Required, calloutEnabled: false
      });
      a.blockId = b.id;
      self.placeAnns.push(a); self.byBlock[b.id] = a;
    });
    map.addAnnotations(this.placeAnns);
  };

  // fitFocusedDay: the stops' spread x1.6 with a ~9 km floor
  TripMap.prototype.regionForDay = function (i) {
    var day = this.trip.days[i];
    var pts = day.blocks.filter(function (b) { return b.mapPlace; }).map(function (b) { return { lat: b.mapPlace.latitude, lon: b.mapPlace.longitude }; });
    var center, latSpan = 0, lonSpan = 0;
    if (!pts.length) center = { lat: day.latitude, lon: day.longitude };
    else {
      var lats = pts.map(function (p) { return p.lat; }), lons = pts.map(function (p) { return p.lon; });
      var a = Math.min.apply(null, lats), b = Math.max.apply(null, lats), c = Math.min.apply(null, lons), d = Math.max.apply(null, lons);
      center = { lat: (a + b) / 2, lon: (c + d) / 2 }; latSpan = b - a; lonSpan = d - c;
    }
    var min = 0.08;
    return new mapkit.CoordinateRegion(coord(center), new mapkit.CoordinateSpan(Math.max(latSpan * 1.6, min), Math.max(lonSpan * 1.6, min)));
  };

  // focus(dayIndex): what the app does when the timeline pages to a new day
  TripMap.prototype.focus = function (i, animated) {
    if (i === this.focused) return;
    var prev = this.lastGlide, day = this.trip.days[i];
    this.focused = i;
    this.buildCities();
    this.buildPlaces();
    var target = this.regionForDay(i).toMapRect(), map = this.map;
    var here = { lat: day.latitude, lon: day.longitude };
    var hop = prev && (Math.abs(prev.lat - here.lat) > 0.0005 || Math.abs(prev.lon - here.lon) > 0.0005);
    this.lastGlide = here;
    if (animated !== false && hop) {
      // glideTo: pull back over the midpoint, then descend onto the new city.
      var both = new mapkit.BoundingRegion(Math.max(prev.lat, here.lat), Math.max(prev.lon, here.lon),
        Math.min(prev.lat, here.lat), Math.min(prev.lon, here.lon)).toCoordinateRegion();
      both.span = new mapkit.CoordinateSpan(both.span.latitudeDelta * 1.6, both.span.longitudeDelta * 1.6);
      map.setVisibleMapRectAnimated(both.toMapRect(), true);
      clearTimeout(this.glideT);
      this.glideT = setTimeout(function () { map.setVisibleMapRectAnimated(target, true); }, 1300);
    } else {
      map.setVisibleMapRectAnimated(target, animated !== false);
    }
  };

  // fitWholeRoute
  TripMap.prototype.overview = function () {
    this.focused = -1; this.lastGlide = null;
    this.buildCities();
    if (this.placeAnns.length) { this.map.removeAnnotations(this.placeAnns); this.placeAnns = []; this.byBlock = {}; }
    var lats = this.route.map(function (p) { return p.lat; }), lons = this.route.map(function (p) { return p.lon; });
    var r = new mapkit.BoundingRegion(Math.max.apply(null, lats), Math.max.apply(null, lons), Math.min.apply(null, lats), Math.min.apply(null, lons)).toCoordinateRegion();
    r.span = new mapkit.CoordinateSpan(r.span.latitudeDelta * 1.4, r.span.longitudeDelta * 1.4);
    this.map.setVisibleMapRectAnimated(r.toMapRect(), true);
  };

  // applyHighlight: lift the pin for the entry being read.
  TripMap.prototype.highlight = function (blockId) {
    var self = this;
    this.silent = true;
    this.placeAnns.forEach(function (a) { a.selected = a.blockId === blockId; });
    setTimeout(function () { self.silent = false; }, 0);
  };

  TripMap.prototype.setDark = function (dark) {
    this.map.colorScheme = dark ? mapkit.Map.ColorSchemes.Dark : mapkit.Map.ColorSchemes.Light;
  };

  global.RoamlyTripMap = { TripMap: TripMap, stopNumbers: stopNumbers, timelineBlocks: timelineBlocks };
})(window);
