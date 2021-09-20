interface ActivityObject {
	actStart: string; actEnd: string; inactDuration: number; 
	windowName: string; processName: string;
}
type Activity = ActivityObject[]

function columnSum(activity: Activity, key: string): number {
	// Get SUM() of a column
	// given the column name as a key (string)
	let colSum = 0;
	for (const element of activity) 
		colSum += element[key];
	return colSum
}
function getTotalActivity(activity: Activity): number {

	let total = 0;
	for (const element of activity) {
		let aStart = new Date(element["actStart"]);
		let aEnd = new Date(element["actEnd"]);
		total += (aEnd.valueOf() - aStart.valueOf()) / 1000;}
	return total;
}

(async () => {
	// /data/?period=today
	// let periods = ["today", "24h","3d","7d","1M","3M","6M","1Y","all"]
	// let baseUrl = new URL('http://192.168.254.106:5000/data/')

	let baseUrl = 'http://localhost:5000/data/'
	let url = new URL(baseUrl)

	let period = 'today' 
	// Sets baseUrl/?period='today'
	url.searchParams.set('period', period);
	const data = await fetch(url.toString())
	const activity = (await data.json())["rows"]

	const totalInactivity = columnSum(activity, "inactDuration");
	const totalActivity = getTotalActivity(activity) - totalInactivity;
	
	console.log(`total Activity: ${totalActivity}`)
	console.log(`total inactivity: ${totalInactivity}`)
	console.log(`ratio: ${totalActivity / totalInactivity}`)
	console.log(activity)
	document.body.textContent = <div/>
})();
