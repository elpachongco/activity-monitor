(function () {
    'use strict';

    function getTimesInDay(interval) {
        const absInterval = Math.abs(interval);
        let hours = [];
        let dateTime = (new Date()).setHours(0, 0, 0, 0);
        let intervalMs = (absInterval * 60) * 1000;
        const maxMinutesInDay = 1440;
        for (let minutes = 0; minutes < maxMinutesInDay; minutes += interval) {
            let time = (new Date(dateTime)).toLocaleTimeString();
            hours.push(time);
            dateTime += intervalMs;
        }
        return hours;
    }
    function aSum(a) {
        return a.reduce((prevVal, currVal) => {
            return prevVal + currVal;
        });
    }
    function dtRangeIndex(table, start, end = new Date()) {
        let started = false;
        let ended = false;
        let index = {
            from: null,
            to: null
        };
        let i = 0;
        for (let item of table["actStart"]) {
            let actStart = new Date(item);
            if (actStart >= start && !started) {
                index.from = i;
                started = !started;
            }
            if (started && actStart <= end) {
                index.to = i;
                ended = !ended;
            }
            if (ended && actStart > end)
                break;
            i++;
        }
        return index;
    }
    function dayStart(date = new Date()) {
        let newDate = date.setHours(0, 0, 0, 0);
        return new Date(newDate);
    }
    function getDaysInWeek() {
        return ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];
    }

    let baseUrl = 'http://localhost:5000/data/';
    let url = new URL(baseUrl);
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
        let newActObj = { "actDuration": actDurations };
        return Object.assign(activity, newActObj);
    }
    function main(activity) {
        let actStart = activity["actStart"];
        activity["actEnd"];
        let actDuration = activity["actDuration"];
        let inactDuration = activity["inactDuration"];
        activity["processName"];
        activity["windowName"];
        const hourlyActivity = {
            labels: null,
            data: null
        };
        const dailyActivity = Object.assign({}, hourlyActivity);
        [hourlyActivity.labels, hourlyActivity.data] = (() => {
            let labels = getTimesInDay(60);
            let data = Array(24).fill(0, 0, 24);
            let i = 0;
            let currentHour;
            for (let item of actStart) {
                let dt = new Date(item);
                currentHour = dt.getHours();
                data[currentHour] += actDuration[i];
                i++;
            }
            return [labels, data];
        })();
        [dailyActivity.labels, dailyActivity.data] = (() => {
            let labels = getDaysInWeek();
            let data = Array(7).fill(0);
            let i = 0;
            let weekDay;
            for (let item of actStart) {
                let dt = new Date(item);
                weekDay = dt.getDay();
                data[weekDay] += actDuration[i];
                i++;
            }
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
        const actInact10d = (() => {
            let { from, to } = (() => {
                let currDate = (new Date()).getDate();
                let referenceDay = (new Date()).setDate(currDate - 10);
                return dtRangeIndex(activity, new Date(referenceDay));
            })();
            if (from == null || to == null)
                return;
            let acts = [];
            let inacts = [];
            let labels = [];
            let counter = 0;
            for (let item of actStart.slice(from, to + 1)) {
                let dtString = (new Date(item)).toDateString();
                let activityIndex = from + counter;
                if (counter === 0) {
                    labels.push(dtString);
                    acts.push(actDuration[activityIndex]);
                    inacts.push(inactDuration[activityIndex]);
                }
                if (dtString === labels[labels.length - 1]) {
                    acts[acts.length - 1] += actDuration[activityIndex];
                    inacts[inacts.length - 1] += inactDuration[activityIndex];
                }
                else {
                    acts.push(actDuration[activityIndex]);
                    inacts.push(inactDuration[activityIndex]);
                    labels.push(dtString);
                }
                counter++;
            }
            return { acts, inacts, labels };
        })();
        console.log(hourlyActivity);
        console.log(dailyActivity);
        console.log(actVsInact - 100);
        console.log(actInact10d);
    }

})();
