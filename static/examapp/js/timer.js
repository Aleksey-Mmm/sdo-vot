
var mydata = JSON.parse(document.getElementById('mydata').textContent)
mydata = mydata.split('"').join('')
const end = Date.parse(mydata)
const coundownBox = document.getElementById('coundown-box')

setInterval(()=>{
    const now = new Date().getTime()
    const diff = end - now
    const m = Math.floor((diff / (1000 * 60)) % 60)
    const s = Math.floor((diff / 1000) % 60)
    const h = Math.floor((diff / (1000 * 60 * 60)) % 24)
    if (diff>0) {
        if ((m<10) && (s<10)) {
            coundownBox.innerHTML = '0' + h + ' ч 0' + m + ' мин 0' + s + ' сек'
        } else if (s<10) {
            coundownBox.innerHTML = '0' + h + ' ч ' + m + ' мин 0' + s + ' сек'
        } else if (m<10) {
            coundownBox.innerHTML = '0' + h + ' ч 0' + m + ' мин ' + s + ' сек'
        } else {
            coundownBox.innerHTML = '0' + h + ' ч ' + m + ' мин ' + s+ ' сек'
        }
    }
}, 1000)
