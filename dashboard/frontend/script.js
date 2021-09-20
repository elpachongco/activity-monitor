"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
function columnSum(activity, key) {
    // Get SUM() of a column
    // given the column name as a key (string)
    let colSum = 0;
    for (const element of activity)
        colSum += element[key];
    return colSum;
}
function getTotalActivity(activity) {
    let total = 0;
    for (const element of activity) {
        let aStart = new Date(element["actStart"]);
        let aEnd = new Date(element["actEnd"]);
        total += (aEnd.valueOf() - aStart.valueOf()) / 1000;
    }
    return total;
}
(() => __awaiter(void 0, void 0, void 0, function* () {
    // /data/?period=today
    // let periods = ["today", "24h","3d","7d","1M","3M","6M","1Y","all"]
    // let baseUrl = new URL('http://192.168.254.106:5000/data/')
    let baseUrl = 'http://localhost:5000/data/';
    let url = new URL(baseUrl);
    let period = 'today';
    // Sets baseUrl/?period='today'
    url.searchParams.set('period', period);
    const data = yield fetch(url.toString());
    const activity = (yield data.json())["rows"];
    const totalInactivity = columnSum(activity, "inactDuration");
    const totalActivity = getTotalActivity(activity) - totalInactivity;
    console.log(`total Activity: ${totalActivity}`);
    console.log(`total inactivity: ${totalInactivity}`);
    console.log(`ratio: ${totalActivity / totalInactivity}`);
    console.log(activity);
    document.body.textContent = React.createElement("div", null);
}))();
