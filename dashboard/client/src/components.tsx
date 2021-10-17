import { Props, GraphData } from "./types";
// import { dayStart } from "./utils";

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
    props!: {
		data: {
			durs: number[],
			labels: Date[]
		}
	}; 
	// date: Date;

	constructor(props: Props) 
	{
		super(props);
		// this.date = dayStart();
	}

	render() {

		let squares: any = []

		let normalizedDurs = ((durs) => {
			let maxDur = Math.max(...durs)
			let minDur = Math.min(...durs)

			let normalized: number[] = []
			durs.map((dur) => {
				let norm = (dur - minDur) / (maxDur - minDur)
				normalized.push( Math.round(norm*100) )
			})
			return normalized
		})(this.props.data.durs)

		// let lut = ["a","b","c","d","e","f"]

		console.log(normalizedDurs)

		let column = 0
		let row = 0
		for (let i=0; i < 364; i++) {

			// bruh
			let color = 0;
			if (normalizedDurs[i] < 100/6) color = 0;
			else if ( normalizedDurs[i] < ((100/6) * 2) ) color = 1;
			else if ( normalizedDurs[i] < ((100/6) * 3) ) color = 2;
			else if ( normalizedDurs[i] < ((100/6) * 4) ) color = 3;
			else if ( normalizedDurs[i] < ((100/6) * 5) ) color = 4;
			else if ( normalizedDurs[i] < ((100/6) * 6) ) color = 5;

			squares.push(
				<rect className={`num-${i} color-${color}`} 
				key={i.toString()} />
			)
		}

		return (
			// 364 squares from today to past year in 7 columns
			// Vary each color to 8 levels of intensity depending on time
			<div className="calendarView">
				<svg>
					{squares}
				</svg>
			</div>	
		);
	}
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

				<CalendarView data={this.props.data.calendar}/>

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