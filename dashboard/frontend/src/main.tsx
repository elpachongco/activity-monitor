import  {
	getDaysInWeek, getTimesInDay, aSum, dtRangeIndex, dayStart,
	includes, isTable } from "./utils";
import { Dashboard } from "./components";
import { RawActivity, Activity, React, ReactDOM} from "./types";

// let periods = ["today", "24h","3d","7d","1M","3M","6M","1Y","all"]


let baseUrl = 'http://localhost:5000/data/'
let url = new URL(baseUrl)
url.searchParams.set('period', "all");

fetch(url.toString())
    .then(response => response.json())
    .then(data => getActDuration(data))
    .then(activity => main(activity))

function getActDuration(activity: RawActivity): Activity
{
    let actDurations = activity["actStart"].map( 
        (item: string, i: number) => {
            let start = new Date(item);
            let end = new Date(activity["actEnd"][i]);
            let duration =  (end.valueOf() - start.valueOf()) / 1000;
            return duration - activity["inactDuration"][i];
        });

    // let newActObj: { "actDuration": number[] };
    let newActObj = { "actDuration":  actDurations }

    return Object.assign(activity, newActObj);
}

interface ChartData { labels: null | string[], data: null | number[] }    

function main(activity: Activity): void
{

    let actStart = activity["actStart"]  
    let actDuration = activity["actDuration"]
    let inactDuration = activity["inactDuration"]

    const hourlyActivity: ChartData = { 
        labels: null,
        data: null
    };
    // clone (instead of copying reference) 
    const dailyActivity = { ...hourlyActivity };

    // Get most active hours in a day, todo: except today
    [ hourlyActivity.labels, hourlyActivity.data ] = (() => {

        let labels = getTimesInDay(60);
        let data = Array(24).fill(0, 0, 24);
        // Loop through days in the table
        let i = 0;
        let currentHour;
        for (let item of actStart) {
            let dt = new Date(item);
            currentHour = dt.getHours();
            data[currentHour] += actDuration[i];
            i++;
        };
        return [labels, data];
    })();

    // Get most active days in a week: except this week
    [ dailyActivity.labels, dailyActivity.data ] = (() => {

        let labels = getDaysInWeek();
        let data = Array(7).fill(0);
        // Loop through days in the table
        let i = 0;
        let weekDay;
        for (let item of actStart) {
            let dt = new Date(item);
            weekDay = dt.getDay();
            data[weekDay] += actDuration[i];
            i++;
        };
        return [labels, data];
    })();

    const actVsInact = ( () => {

        let entriesToday =  dtRangeIndex(activity, dayStart())
        let [iFrom, iTo] = [entriesToday.from, entriesToday.to]
        if (iFrom == null || iTo == null) return 0
        let todayAct = actDuration.slice(iFrom, iTo + 1)
        let todayInact = inactDuration.slice(iFrom, iTo + 1)       
        let totalAct = aSum(todayAct) 
        let totalInact = aSum(todayInact)

        return 100 * (totalAct / totalInact);
    } )();

    const actInact10d = ( () => {

        let {from, to} = ( () => {
            let currDate = (new Date()).getDate();
            let referenceDay = (new Date()).setDate(currDate - 10);       
            return dtRangeIndex(activity, new Date(referenceDay)) 
        })()

        if (from == null || to == null) return;

        let acts = []; let inacts = []; let labels = []; 
        let counter = 0;

        for ( let item of actStart.slice(from, to + 1) ) {

            let dtString = (new Date(item)).toDateString()
            let activityIndex = from + counter
            if (counter === 0) { 
                labels.push(dtString)
                acts.push(actDuration[activityIndex])
                inacts.push(inactDuration[activityIndex])
            }

            if (dtString === labels[labels.length-1]) {
                acts[acts.length-1] += actDuration[activityIndex]
                inacts[inacts.length-1] += inactDuration[activityIndex]
            } else {
                acts.push(actDuration[activityIndex])
                inacts.push(inactDuration[activityIndex])
                labels.push(dtString)
            }
            counter++;
        }
        return { acts, inacts, labels }

    } )();

    console.log(hourlyActivity);
    console.log(dailyActivity);
    console.log(actVsInact - 100);
    console.log(actInact10d);

    const data = {
        hourlyActivity,
        dailyActivity,
        actVsInact,
        actInact10d
    }  

    ReactDOM.render(
        <Dashboard data={data}/>, 
        document.getElementById('root')
    );
}