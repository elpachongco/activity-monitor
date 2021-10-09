import { Props, GraphData } from "./types";
// import { React, Props, Chart} from "./types";

function Header() {
	return (
			<div className="header">
				<p className="title">Activity Report 🌞</p>
				<p> 
					This program logs user activity based on the foreground 
					window name. Inactivity is also monitored for each program 
					based on input activity. The data is uploaded to an sqlite 
					database. 
				</p>
			</div>
	);
}

class Graph extends React.Component {
    props: any;
    canvasRef: any;

	constructor(props: Props) 
	{
		super(props);
		this.canvasRef = React.createRef();
	}

	createGraph() {
		const config = {
			type: this.props.type,
			data: this.props.data,
			options: this.props.options
		}
		new Chart(this.canvasRef.current, config);
	}
	componentDidMount() {
		this.createGraph();
	}

	render() {
		return (
			<div className="graph">
				<canvas ref={this.canvasRef}></canvas>
			</div>
		)
	}
}

export class Dashboard extends React.Component {
    props: any;
	ratio10d: GraphData;
	actVsInact: GraphData;

	constructor(props: Props)
	{
		super(props)
		const data = this.props.data
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
				data: [data.actVsInact, (100 - data.actVsInact)] ,
				backgroundColor: ['#b7e1cd', '#949495'],
				borderColor: null,
			}
			]
		 
		};
	}
	componentDidMount() {
	}

	render() {
		return (
			<div className="dashboard">

				<Header />

				<div className="card ratio">
					<h2>10-Day Activity / Inactivity Ratio</h2>
					<Graph type="line" data={this.ratio10d}/>
				</div>

				<div className="card doughnut">
					<h2>Active vs Inactive Time Today</h2>
					<Graph type="doughnut" data={this.actVsInact}/>
				</div>

			</div>
		);
	}
}