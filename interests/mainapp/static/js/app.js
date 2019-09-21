console.log(`        
(_)     | |                   | |      
 _ _ __ | |_ ___ _ __ ___  ___| |_ ___ 
| | '_ \| __/ _ \ '__/ _ \/ __| __/ __|
| | | | | ||  __/ | |  __/\__ \ |_\__ \
|_|_| |_|\__\___|_|  \___||___/\__|___/
`);




console.log('Hello');                                  



function openNav() {
    document.getElementById("mySidenav").style.width = "400px";
  }
  
  /* Set the width of the side navigation to 0 */
  function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
  }
  // document.getElementById("ie").style.display = "none"; 

function demoDisplay() {
document.getElementById("ie").style.display = "none";
}



 /* if (GetIEVersion() > 0){
    document.getElementById("ie").style.display = "block";
 }
 else{
  document.getElementById("ie").style.display = "none";
 } */
//  function GetIEVersion() {
//     var sAgent = window.navigator.userAgent;
//     var Idx = sAgent.indexOf("MSIE");
  
//     // If IE, return version number.
//     if (Idx > 0){
//       return parseInt(sAgent.substring(Idx+ 5, sAgent.indexOf(".", Idx)));
//     }
//     // If IE 11 then look for Updated user agent string.
//     else if (!!navigator.userAgent.match(/Trident\/7\./)){
//       return 11;
//     }
//     else{
//       return 0; //It is not IE
//     }
//   }
  
//   var ie = document.getElementById('ie');
//   var e2 = document.getElementById('chrome');
  
//   if (GetIEVersion() > 0){
//      alert("This is IE " + GetIEVersion());
//      ie.style.display = 'block';
//      e2.style.display = 'none';
//   }
//   else{
//      alert("This is not IE.");
//      ie.style.display = 'none';
//      e2.style.display = 'block';
//   }