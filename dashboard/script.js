// let baseUrl = new URL('http://192.168.254.106:5000/data/')
let baseUrl = new URL('http://localhost:5000/data/')
let url = new URL(baseUrl)

// /data/?period=today
url.searchParams.set('period', 'today')

let x = document.getElementById("ff")

let periods = ["today", "24h","3d","7d","1M","3M","6M","1Y","ALL"]

let period = 'today'

// Create a period selector

// async function getActivityData(url) {
    // let response = fetch(url)
    // let data = await response.json()
    // return data
// }
// let i = getActivityData(url)
// console.log(i)

fetch(url)
    .then(response => response.json())
    .then(data => {
        x.textContent = data["rows"][0]
    })