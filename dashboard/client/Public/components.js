import { normalize } from "./utils.js";
function Header() {
    return (React.createElement("div", { className: "header" },
        React.createElement("p", { className: "title" }, "Activity Report \uD83C\uDF1E"),
        React.createElement("p", null, "This program logs user activity based on the foreground window name. Inactivity is also monitored for each program based on input activity. The data is uploaded to an sqlite database.")));
}
/**
 * Github style calendar view.
 *
 * durs - array of number of length 364. Contains activity durations for
 * each day, From today to 364 days ago.
 *
 * labels - array of dates of the corresponding numbers
 *
 * @returns Full calendar view component
 */
class CalendarView extends React.Component {
    // date: Date;
    constructor(props) {
        super(props);
        // this.date = dayStart();
    }
    render() {
        let squares = [];
        // let normalizedDurs = ((durs) => {
        // 	let maxDur = Math.max(...durs)
        // 	let minDur = Math.min(...durs)
        // 	let normalized: number[] = []
        // 	durs.map((dur) => {
        // 		let norm = (dur - minDur) / (maxDur - minDur)
        // 		normalized.push( Math.round(norm*100) )
        // 	})
        // 	return normalized
        // })(this.props.data.durs)
        let normalizedDurs = normalize(this.props.data.durs, 100);
        for (let i = 0; i < 364; i++) {
            // bruh
            let color = 0;
            if (normalizedDurs[i] < 100 / 6)
                color = 0;
            else if (normalizedDurs[i] < ((100 / 6) * 2))
                color = 1;
            else if (normalizedDurs[i] < ((100 / 6) * 3))
                color = 2;
            else if (normalizedDurs[i] < ((100 / 6) * 4))
                color = 3;
            else if (normalizedDurs[i] < ((100 / 6) * 5))
                color = 4;
            else if (normalizedDurs[i] < ((100 / 6) * 6))
                color = 5;
            squares.push(React.createElement("rect", { className: `num-${i} color-${color}`, key: i.toString() }));
        }
        return (
        // 364 squares from today to past year in 7 columns
        // Vary each color to 8 levels of intensity depending on time
        React.createElement("div", { className: "calendarView card" },
            React.createElement("svg", null,
                React.createElement("g", { className: "squares" }, squares))));
    }
}
class WordCloud extends React.Component {
    constructor(props) {
        super(props);
        let tempCounts = [];
        this.words = this.props.data.map((item) => {
            tempCounts.push(item[1]);
            return item[0];
        });
        this.counts = normalize(tempCounts);
    }
    render() {
        let dataLen = this.words.length;
        let texts = [];
        for (let i = 0; i <= this.props.maxAmount; i++) {
            let j = dataLen - i;
            texts.push(React.createElement("text", { dx: "50%", x: "50%", "font-size": "25px", fill: "white" }, this.words[j]));
        }
        return (React.createElement("div", { className: "card wordcloud" },
            React.createElement("svg", { viewbox: "200 -35 240 80" }, texts)));
    }
}
class Graph extends React.Component {
    constructor(props) {
        super(props);
        this.canvasRef = React.createRef();
    }
    createGraph() {
        const config = {
            type: this.props.type,
            data: this.props.data,
            options: this.props.options
            // options: {
            // backgroundColor: "#ffffff"
            // }
        };
        new Chart(this.canvasRef.current, config);
    }
    componentDidMount() {
        this.createGraph();
    }
    render() {
        return (React.createElement("div", { className: "graph" },
            React.createElement("canvas", { ref: this.canvasRef })));
    }
}
export class Dashboard extends React.Component {
    constructor(props) {
        super(props);
        const data = this.props.data;
        this.linegraph = {
            labels: data.linegraph.labels,
            datasets: [
                {
                    label: 'Activity',
                    backgroundColor: 'rgb(255, 99, 132)',
                    borderColor: 'rgb(255, 99, 132)',
                    data: data.linegraph.acts,
                    tension: 0.28
                },
                {
                    label: 'Inactivity',
                    backgroundColor: 'rgb(255, 99, 132)',
                    borderColor: 'rgb(255, 99, 132)',
                    data: data.linegraph.inacts,
                    tension: 0.28
                },
                {
                    label: 'Day Length',
                    backgroundColor: 'rgb(255, 99, 132)',
                    borderColor: 'rgb(255, 99, 132)',
                    data: data.linegraph.dayLen,
                    tension: 0.28
                }
            ]
        };
        this.actVsInact = {
            labels: ["Activity", "Inactivity"],
            datasets: [
                {
                    label: "Today's activity vs inactivity",
                    data: [data.actVsInact, (100 - data.actVsInact)],
                    backgroundColor: ['#b7e1cd', '#949495'],
                    borderColor: null,
                }
            ]
        };
        this.histogram = {
            labels: data.histogram.labels,
            datasets: [
                {
                    barPercentage: 1,
                    categoryPercentage: 1,
                    label: "Activity Duration",
                    data: data.histogram.data,
                    backgroundColor: '#949495',
                    borderColor: null,
                }
            ]
        };
        this.calendar = data.calendar;
        this.wordCloud = data.wordCloud;
    }
    componentDidMount() {
    }
    render() {
        return (React.createElement("div", { className: "dashboard" },
            React.createElement(Header, null),
            React.createElement(CalendarView, { data: this.calendar }),
            React.createElement("div", { className: "card ratio" },
                React.createElement("h2", null, " 30-day Activity / Inactivity"),
                React.createElement(Graph, { type: "line", data: this.linegraph })),
            React.createElement("div", { className: "card doughnut" },
                React.createElement("h2", null, "Active vs Inactive Time Today"),
                React.createElement(Graph, { type: "doughnut", data: this.actVsInact })),
            React.createElement("div", { className: "card histogram" },
                React.createElement("h2", null, "Total active time per hour"),
                React.createElement(Graph, { type: "bar", data: this.histogram })),
            React.createElement(WordCloud, { data: this.wordCloud, maxAmount: 35 })));
    }
}
