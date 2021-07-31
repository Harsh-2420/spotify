
// mapboxgl.accessToken = 'pk.eyJ1IjoiaGFyc2gtaiIsImEiOiJja3JraHRmMnEzbnA1MndwOGI2OTY1enNrIn0.Lrx1G8lFIKLt_7OsC6ow7g';

// var geojson = {
//   'type': 'FeatureCollection',
//   'features': [
//     {
//       'type': 'Feature',
//       'geometry': {
//         'type': 'Point',
//         'coordinates': [-77.032, 38.913]
//       },
//       'properties': {
//         'title': 'Mapbox',
//         'description': 'Washington, D.C.'
//       }
//     },
//     {
//       'type': 'Feature',
//       'geometry': {
//         'type': 'Point',
//         'coordinates': [-122.414, 37.776]
//       },
//       'properties': {
//         'title': 'Mapbox',
//         'description': 'San Francisco, California'
//       }
//     }
//   ]
// };

// var map = new mapboxgl.Map({
//   container: 'map',
//   style: 'mapbox://styles/mapbox/light-v10',
//   center: [-96, 37.8],
//   zoom: 3
// });

// // add markers to map
// geojson.features.forEach(function (marker) {
//   // create a HTML element for each feature
//   var el = document.createElement('div');
//   el.className = 'marker';

//   // make a marker for each feature and add it to the map
//   new mapboxgl.Marker(el)
//     .setLngLat(marker.geometry.coordinates)
//     .setPopup(
//       new mapboxgl.Popup({ offset: 25 }) // add popups
//         .setHTML(
//           '<h3>' +
//             marker.properties.title +
//             '</h3><p>' +
//             marker.properties.description +
//             '</p>'
//         )
//     )
//     .addTo(map);
// });







// (function() {
//   "use strict";

//   window.addEventListener('load', () => {
//     on_page_load()
//   });

//   /**
//    * Function gets called when page is loaded.
//    */
//   function on_page_load() {
//     // Initialize On-scroll Animations
//     AOS.init({
//       anchorPlacement: 'top-left',
//       duration: 600,
//       easing: "ease-in-out",
//       once: true,
//       mirror: false,
//       disable: 'mobile'
//     });
//   }

//   /**
//    * Navbar effects and scrolltop buttons upon scrolling
//    */
//   const navbar = document.getElementById('header-nav')
//   var body = document.getElementsByTagName("body")[0]
//   const scrollTop = document.getElementById('scrolltop')
//   window.onscroll = () => {
//     if (window.scrollY > 0) {
//       navbar.classList.add('fixed-top', 'shadow-sm')
//       body.style.paddingTop = navbar.offsetHeight + "px"
//       scrollTop.style.visibility = "visible";
//       scrollTop.style.opacity = 1;
//     } else {
//       navbar.classList.remove('fixed-top', 'shadow-sm')
//       body.style.paddingTop = "0px"
//       scrollTop.style.visibility = "hidden";
//       scrollTop.style.opacity = 0;
//     }
//   };

//   /**
//    * Masonry Grid
//    */
//   var elem = document.querySelector('.grid');
//   if(elem) {
//     imagesLoaded(elem, function() {
//       new Masonry(elem, {
//         itemSelector: '.grid-item',
//         percentPosition: true,
//         horizontalOrder: true
//       });
//     })
//   }

//   /**
//    * Big Picture Popup for images and videos
//    */
//    document.querySelectorAll("[data-bigpicture]").forEach((function(e) {
//      e.addEventListener("click", (function(t){
//        t.preventDefault();
//        const data =JSON.parse(e.dataset.bigpicture)
//        BigPicture({
//         el: t.target,
//         ...data
//       })
//      })
//     )
//   }))

//   /**
//    * Big Picture Popup for Photo Gallary
//    */
//    document.querySelectorAll(".bp-gallery a").forEach((function(e) {
//     var caption = e.querySelector('figcaption')
//     var img = e.querySelector('img')
//     // set the link present on the item to the caption in full view
//     img.dataset.caption = '<a class="link-light" target="_blank" href="' + e.href + '">' + caption.innerHTML + '</a>';
//     window.console.log(caption, img)
//      e.addEventListener("click", (function(t){
//        t.preventDefault();
//        BigPicture({
//         el: t.target,
//         gallery: '.bp-gallery',
//       })
//      })
//     )
//   }))

//   // Add your javascript here


// })();

