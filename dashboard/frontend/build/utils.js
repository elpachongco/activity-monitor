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
;
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
        ;
        if (started && actStart <= end) {
            index.to = i;
            ended = !ended;
        }
        ;
        if (ended && actStart > end)
            break;
        i++;
    }
    ;
    return index;
}
;
function isTable(table) {
    let keys = Object.keys(table);
    if (keys.length < 1)
        return false;
    let rowCount = table[keys[0]].length;
    for (const key of keys)
        if (table[key] != rowCount)
            return false;
    return true;
}
function dayStart(date = new Date()) {
    let newDate = date.setHours(0, 0, 0, 0);
    return new Date(newDate);
}
function includes(obj, arr) {
    for (let item in arr) {
        if (obj === item)
            return true;
    }
    return false;
}
function getDaysInWeek() {
    return ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];
}
export { getDaysInWeek, getTimesInDay, aSum, includes, dtRangeIndex, isTable, dayStart };
