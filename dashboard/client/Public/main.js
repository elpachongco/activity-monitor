import { getDaysInWeek, getTimesInDay, aSum, dtRangeIndex, dayStart } from "./utils.js";
import { Dashboard } from "./components.js";
// let periods = ["today", "24h","3d","7d","1M","3M","6M","1Y","all"]
// let baseUrl = 'http://localhost:5000/data/'
let url = new URL(`http://${window.location.host}/data/`);
url.searchParams.set('period', "all");
fetch(url.toString())
    .then(response => response.json())
    .then(data => getActDuration(data))
    .then(activity => main(activity));
function getActDuration(activity) {
    let actDurations = activity["actStart"].map((item, i) => {
        let start = new Date(item);
        let end = new Date(activity["actEnd"][i]);
        let duration = (end.valueOf() - start.valueOf()) / 1000;
        return duration - activity["inactDuration"][i];
    });
    // let newActObj: { "actDuration": number[] };
    let newActObj = { "actDuration": actDurations };
    return Object.assign(activity, newActObj);
}
function main(activity) {
    let actStart = activity["actStart"];
    let actDuration = activity["actDuration"];
    let inactDuration = activity["inactDuration"];
    const hourlyActivity = {
        labels: null,
        data: null
    };
    // clone (instead of copying reference) 
    const dailyActivity = Object.assign({}, hourlyActivity);
    // Get most active hours in a day, todo: except today
    [hourlyActivity.labels, hourlyActivity.data] = (() => {
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
        }
        ;
        return [labels, data];
    })();
    // Get most active days in a week: except this week
    [dailyActivity.labels, dailyActivity.data] = (() => {
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
        }
        ;
        return [labels, data];
    })();
    const actVsInact = (() => {
        let entriesToday = dtRangeIndex(activity, dayStart());
        let [iFrom, iTo] = [entriesToday.from, entriesToday.to];
        if (iFrom == null || iTo == null)
            return 0;
        let todayAct = actDuration.slice(iFrom, iTo + 1);
        let todayInact = inactDuration.slice(iFrom, iTo + 1);
        let totalAct = aSum(todayAct);
        let totalInact = aSum(todayInact);
        return 100 * (totalAct / totalInact);
    })();
    const ratio10d = (() => {
        let { from, to } = (() => {
            let currDate = (new Date()).getDate();
            let referenceDay = (new Date()).setDate(currDate - 30);
            return dtRangeIndex(activity, new Date(referenceDay));
        })();
        if (from == null || to == null)
            return;
        let acts = 0;
        let inacts = 0;
        let labels = [];
        let ratio = [];
        let counter = 0;
        for (let item of actStart.slice(from, to + 1)) {
            let dtString = (new Date(item)).toDateString();
            // ommit year
            dtString = dtString.slice(0, 10);
            let activityIndex = from + counter;
            if (counter === 0) {
                labels.push(dtString);
                acts = actDuration[activityIndex];
                inacts = inactDuration[activityIndex];
            }
            if (dtString === labels[labels.length - 1]) {
                acts += actDuration[activityIndex];
                inacts += inactDuration[activityIndex];
            }
            else {
                ratio.push(acts / inacts);
                labels.push(dtString);
                acts = inacts = 0;
            }
            counter++;
        }
        return { ratio, labels };
    })();
    console.log("hourly activity:", hourlyActivity);
    console.log("daily activity:", dailyActivity);
    console.log("act vs inact:", actVsInact - 100);
    console.log("10d act inact", ratio10d);
    const calendar = (() => {
        let day = 24 * 60 * 60 * 1000;
        let year = 364 * day;
        let yearAgo = dayStart().valueOf() - year;
        let durs = Array(364).fill(0);
        let labels = [];
        for (let i = 0; i < 364; i++) {
            let dt = new Date(yearAgo + (day * i));
            labels.push(dt);
            if (dt < new Date(actStart[0]))
                continue;
            let dtTomorrow = new Date(dt.valueOf() + day);
            actStart.map((item, j) => {
                let timeStamp = new Date(item);
                if (timeStamp > dt && timeStamp < dtTomorrow) {
                    durs[i] += actDuration[j];
                }
            });
        }
        console.log({ durs, labels });
        return { durs, labels };
    })();
    const data = {
        hourlyActivity,
        dailyActivity,
        actVsInact,
        ratio10d,
        calendar
    };
    ReactDOM.render(React.createElement(Dashboard, { data: data }), document.getElementById('root'));
}
