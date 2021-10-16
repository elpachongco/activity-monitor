// import { dayStart } from "./utils";
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
        let normalizedDurs = ((durs) => {
            let maxDur = Math.max(...durs);
            let minDur = Math.min(...durs);
            let normalized = [];
            durs.map((dur) => {
                let norm = (dur - minDur) / (maxDur - minDur);
                normalized.push(Math.round(norm * 100));
            });
            return normalized;
        })(this.props.data.durs);
        let lut = ["a", "b", "c", "d", "e", "f"];
        console.log(normalizedDurs);
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
            squares.push(React.createElement("div", { className: `square ${lut[color]}`, key: i.toString() }));
        }
        return (
        // 364 squares from today to past year in 7 columns
        // Vary each color to 8 levels of intensity depending on time
        React.createElement("div", { className: "calendarView" }, squares));
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
        this.ratio10d = {
            labels: data.ratio10d.labels,
            datasets: [
                {
                    label: 'Activity time / Inactivity time',
                    backgroundColor: 'rgb(255, 99, 132)',
                    borderColor: 'rgb(255, 99, 132)',
                    data: data.ratio10d.ratio,
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
    }
    componentDidMount() {
    }
    render() {
        return (React.createElement("div", { className: "dashboard" },
            React.createElement(Header, null),
            React.createElement(CalendarView, { data: this.props.data.calendar }),
            React.createElement("div", { className: "card ratio" },
                React.createElement("h2", null, "10-Day Activity / Inactivity Ratio"),
                React.createElement(Graph, { type: "line", data: this.ratio10d })),
            React.createElement("div", { className: "card doughnut" },
                React.createElement("h2", null, "Active vs Inactive Time Today"),
                React.createElement(Graph, { type: "doughnut", data: this.actVsInact }))));
    }
}
