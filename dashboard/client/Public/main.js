import { getTimesInDay, aSum, dtRangeIndex, dayStart, stringToArray } from "./utils.js";
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
    let actEnd = activity["actEnd"];
    let actDuration = activity["actDuration"];
    let inactDuration = activity["inactDuration"];
    // const hourlyActivity: ChartData = { 
    //     labels: null,
    //     data: null
    // };
    // // clone (instead of copying reference) 
    // const dailyActivity = { ...hourlyActivity };
    // // Get most active hours in a day, todo: except today
    // [ hourlyActivity.labels, hourlyActivity.data ] = (() => {
    //     let labels = getTimesInDay(60);
    //     let data = Array(24).fill(0, 0, 24);
    //     // Loop through days in the table
    //     let i = 0;
    //     let currentHour;
    //     for (let item of actStart) {
    //         let dt = new Date(item);
    //         currentHour = dt.getHours();
    //         data[currentHour] += actDuration[i];
    //         i++;
    //     };
    //     return [labels, data];
    // })();
    // // Get most active days in a week: except this week
    // [ dailyActivity.labels, dailyActivity.data ] = (() => {
    //     let labels = getDaysInWeek();
    //     let data = Array(7).fill(0);
    //     // Loop through days in the table
    //     let i = 0;
    //     let weekDay;
    //     for (let item of actStart) {
    //         let dt = new Date(item);
    //         weekDay = dt.getDay();
    //         data[weekDay] += actDuration[i];
    //         i++;
    //     };
    //     return [labels, data];
    // })();
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
    let linegraph = ((days) => {
        let { from, to } = (() => {
            let currDate = (new Date()).getDate();
            let referenceDay = (new Date()).setDate(currDate - days);
            return dtRangeIndex(activity, new Date(referenceDay));
        })();
        if (from == null || to == null)
            return;
        let labels = [];
        let acts = [];
        let inacts = [];
        let dayLen = [];
        let counter = 0;
        let act = 0;
        let inact = 0;
        let len = 0;
        for (let item of actStart.slice(from, to + 1)) {
            let dtString = (new Date(item)).toDateString();
            // ommit year
            dtString = dtString.slice(0, 10);
            let activityIndex = from + counter;
            if (counter == 0) {
                labels.push(dtString);
                act = actDuration[activityIndex] / 60;
                inact = inactDuration[activityIndex] / 60;
                len = new Date(actStart[activityIndex]).valueOf();
                // dayLen.push(len)
            }
            if (dtString == labels[labels.length - 1]) {
                act += (actDuration[activityIndex] / 60);
                inact += (inactDuration[activityIndex] / 60);
            }
            else {
                acts.push(act);
                inacts.push(inact);
                labels.push(dtString);
                len = new Date(actEnd[activityIndex - 1]).valueOf() - len;
                dayLen.push((len / 1000) / 60);
                len = new Date(actStart[activityIndex]).valueOf();
                act = inact = 0;
            }
            counter++;
        }
        // return { ratio, labels }
        return { acts, inacts, labels, dayLen };
    })(45);
    let histogram = (() => {
        let labels = getTimesInDay(60);
        let data = Array(24).fill(0);
        actDuration.map((item, index) => {
            let hour = (new Date(actStart[index])).getHours();
            data[hour] += item;
        });
        return { data, labels };
    })();
    let calendar = (() => {
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
        return { durs, labels };
    })();
    // Returned array is ascending
    let wordCloud = (() => {
        let wordData = {};
        // Loop through window names
        activity["windowName"].map((windowName) => {
            let words;
            // Decompose windowName into an array of words
            words = stringToArray(windowName);
            if (words == null)
                return;
            // Loop through words per window name
            for (const word of words) {
                // append any unique word to object
                if (wordData[word] == null)
                    wordData[word] = 1;
                // For each occurence of word, add to count
                else {
                    wordData[word] += 1;
                }
                ;
            }
        });
        // Sort each word by occurences 
        if (wordData != {}) {
            let wordDataArr = [['', 0]];
            let counter = 0;
            for (let key in wordData) {
                // if (Object.prototype.hasOwnProperty.call(object, key)) {
                // const element = object[key];
                if (counter == 0)
                    wordDataArr = [[key, wordData[key]]];
                wordDataArr.push([key, wordData[key]]);
                counter++;
            }
            let sortedWordData = wordDataArr.sort((first, second) => {
                return first[1] - second[1];
            });
            return sortedWordData;
        }
        return null;
    })();
    // console.log("hourly activity:", hourlyActivity)
    // console.log("daily activity:", dailyActivity)
    console.log("act vs inact:", actVsInact - 100);
    console.log("10d act inact", linegraph);
    console.log("histogram", histogram);
    console.log("calendar", calendar);
    console.log("word cloud", wordCloud);
    const data = {
        // hourlyActivity,
        // dailyActivity,
        actVsInact,
        linegraph,
        calendar,
        histogram,
        wordCloud
    };
    ReactDOM.render(React.createElement(Dashboard, { data: data }), document.getElementById('root'));
}
