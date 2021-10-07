// import { React, Props, Chart} from "./types";
function HeatmapSquare(props) {
    return (React.createElement("div", { className: "heatmap_square", value: props.value }));
}
class Heatmap extends React.Component {
    render() {
        let squares = [];
        for (let i = 0; i < this.props.squares; i++)
            squares.push(React.createElement(HeatmapSquare, { value: i }));
        return (React.createElement("div", { className: "heatmap" }, squares));
    }
}
class Linegraph extends React.Component {
    constructor(props) {
        super(props);
        this.canvasRef = React.createRef();
    }
    createGraph() {
        const labels = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
        ];
        const data = {
            labels: labels,
            datasets: [{
                    label: 'My First dataset',
                    backgroundColor: 'rgb(255, 99, 132)',
                    borderColor: 'rgb(255, 99, 132)',
                    data: [0, 10, 5, 2, 20, 30, 45],
                }]
        };
        const graphConfig = {
            type: 'line',
            data: data,
            options: {}
        };
        new Chart(this.canvasRef.current, graphConfig);
    }
    componentDidMount() {
        this.createGraph();
    }
    render() {
        return (React.createElement("div", { className: "lineGraph" },
            React.createElement("canvas", { id: "graphCanvas", ref: this.canvasRef, width: this.props.width, height: this.props.height })));
    }
}
export class Dashboard extends React.Component {
    componentDidMount() {
    }
    render() {
        return (React.createElement("div", { className: "dashboard" },
            React.createElement(Heatmap, { squares: 25 }),
            React.createElement(Linegraph, { width: 20, height: 20 })));
    }
}
