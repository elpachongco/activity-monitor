// import { React, Props, Chart} from "./types";
function Header() {
    return (React.createElement("div", { className: "header" },
        React.createElement("p", { className: "title" }, "Activity Report \uD83C\uDF1E"),
        React.createElement("p", null, "This program logs user activity based on the foreground window name. Inactivity is also monitored for each program based on input activity. The data is uploaded to an sqlite database.")));
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
            React.createElement("div", { className: "card ratio" },
                React.createElement("h2", null, "10-Day Activity / Inactivity Ratio"),
                React.createElement(Graph, { type: "line", data: this.ratio10d })),
            React.createElement("div", { className: "card doughnut" },
                React.createElement("h2", null, "Active vs Inactive Time Today"),
                React.createElement(Graph, { type: "doughnut", data: this.actVsInact }))));
    }
}
