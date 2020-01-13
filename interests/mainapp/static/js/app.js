// console.log(`        
// (_)     | |                   | |      
//  _ _ __ | |_ ___ _ __ ___  ___| |_ ___ 
// | | '_ \| __/ _ \ '__/ _ \/ __| __/ __|
// | | | | | ||  __/ | |  __/\__ \ |_\__ \
// |_|_| |_|\__\___|_|  \___||___/\__|___/
// `);




var navbar = document.getElementById("sidebar");
var ie = document.getElementById("ie");
var sticky = navbar.offsetTop;


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


function openSearch() {
  document.getElementById("mySearch").style.width = "400px";
}
