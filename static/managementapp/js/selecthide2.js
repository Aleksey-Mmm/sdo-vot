const selectElement = document.querySelector('.selectdisplay');
const votcheck = document.getElementById('votcheck');
const zadachicheck = document.getElementById('zadachicheck');
const elbezrole1 = document.getElementById('elbezrole1');
const elbezrole2 = document.getElementById('elbezrole2');

function modifyDisplay() {
    var e = document.getElementById("selectdisplay");
    var value = e.options[e.selectedIndex].value;
    if (value === "0") {
      votcheck.style.display = 'none';
      zadachicheck.style.display = 'none';
      elbezrole1.style.display = 'none';
      elbezrole2.style.display = 'none';
    } else if (value === "1") {
      votcheck.style.display = 'block';
      zadachicheck.style.display = 'none';
      elbezrole1.style.display = 'none';
      elbezrole2.style.display = 'none';
    } else if (value === "Эксперты") {
      votcheck.style.display = 'none';
      zadachicheck.style.display = 'block';
      elbezrole1.style.display = 'none';
      elbezrole2.style.display = 'none';
    } else if (value === "2") {
      votcheck.style.display = 'block';
      zadachicheck.style.display = 'none';
      elbezrole1.style.display = 'block';
      elbezrole2.style.display = 'block';    
    } else {
      votcheck.style.display = 'none';
      zadachicheck.style.display = 'none';
      elbezrole1.style.display = 'none';
      elbezrole2.style.display = 'none';
    }
  } 

selectElement.addEventListener('change', modifyDisplay);