function convert() {
    let x = document.getElementById('savebutton');
    console.log(x)
    if (x.style.display === "block") {
        x.style.display = "none";
        html2canvas(document.querySelector("#capture"), {
            // width: 1200,
            scale: 1.1,
        }).then(canvas => {
            canvas.toBlob(function(blob) {
                saveAs(blob, "report.png");
            });
        });
        x.style.display = "block";   
    }
  }